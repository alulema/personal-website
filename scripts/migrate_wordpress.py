#!/usr/bin/env python3
"""
WordPress → Astro blog migration script
========================================
Parses a WordPress XML export, converts posts to Markdown,
uploads images to Cloudflare R2, and writes .md files ready
for the Astro Content Collections (blog-en / blog-es).

Usage:
  python scripts/migrate_wordpress.py \
    --xml path/to/wordpress-export.xml \
    --r2-account-id YOUR_ACCOUNT_ID \
    --r2-access-key YOUR_ACCESS_KEY \
    --r2-secret-key YOUR_SECRET_KEY \
    --r2-bucket alexisalulema-media \
    --r2-public-url https://images.alexisalulema.com \
    --lang en \
    --out-dir src/content/blog-en

Dry run (no uploads, no file writes):
  python scripts/migrate_wordpress.py --xml export.xml --dry-run

Requirements:
  pip install -r scripts/requirements-migrate.txt
"""

import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

import boto3
import requests
from botocore.config import Config
from dateutil import parser as dateparser
from markdownify import markdownify as md
from slugify import slugify

# ---------------------------------------------------------------------------
# WordPress XML namespaces
# ---------------------------------------------------------------------------
NS = {
    "wp":      "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _text(element: ET.Element, path: str, ns: dict = NS) -> str:
    el = element.find(path, ns)
    return (el.text or "").strip() if el is not None else ""


def parse_export(xml_path: Path) -> tuple[list[dict], dict[str, str]]:
    """
    Returns (posts, attachments_map).
    attachments_map: { attachment_id -> url }
    posts: list of dicts with raw WordPress data
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Invalid WordPress XML: no <channel> element found.")

    attachments: dict[str, str] = {}
    posts: list[dict] = []

    for item in channel.findall("item"):
        post_type = _text(item, "wp:post_type")
        status = _text(item, "wp:status")

        # Build attachment URL map
        if post_type == "attachment":
            post_id = _text(item, "wp:post_id")
            guid = item.find("guid")
            url = (guid.text or "").strip() if guid is not None else ""
            if post_id and url:
                attachments[post_id] = url
            continue

        if post_type != "post" or status != "publish":
            continue

        # Collect postmeta
        meta: dict[str, str] = {}
        for pm in item.findall("wp:postmeta", NS):
            key = _text(pm, "wp:meta_key")
            val = _text(pm, "wp:meta_value")
            if key:
                meta[key] = val

        # Tags
        tags = [
            cat.text.strip()
            for cat in item.findall("category")
            if cat.get("domain") == "post_tag" and cat.text
        ]

        posts.append({
            "title":       _text(item, "title"),
            "slug":        _text(item, "wp:post_name"),
            "date":        _text(item, "wp:post_date"),
            "content":     _text(item, "content:encoded"),
            "excerpt":     _text(item, "excerpt:encoded"),
            "tags":        tags,
            "thumbnail_id": meta.get("_thumbnail_id", ""),
        })

    return posts, attachments


# ---------------------------------------------------------------------------
# Markdown conversion
# ---------------------------------------------------------------------------

MARKDOWNIFY_OPTIONS = {
    "heading_style": "ATX",
    "bullets": "-",
    "strip": ["script", "style", "iframe"],
}


def html_to_markdown(html: str) -> str:
    # WordPress wraps content in shortcodes and adds [caption] blocks — clean them first
    html = re.sub(r"\[caption[^\]]*\](.*?)\[/caption\]", r"\1", html, flags=re.DOTALL)
    html = re.sub(r"\[[^\]]+\]", "", html)  # remove remaining shortcodes
    converted = md(html, **MARKDOWNIFY_OPTIONS)
    # Collapse 3+ blank lines into 2
    converted = re.sub(r"\n{3,}", "\n\n", converted)
    return converted.strip()


def make_description(excerpt: str, content_html: str) -> str:
    if excerpt:
        return re.sub(r"<[^>]+>", "", excerpt).strip()[:200]
    # Fall back to first non-empty paragraph of content
    text = re.sub(r"<[^>]+>", "", content_html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:200].rstrip(".,;") + "…" if len(text) > 160 else text


# ---------------------------------------------------------------------------
# Image migration
# ---------------------------------------------------------------------------

def _r2_client(account_id: str, access_key: str, secret_key: str):
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def upload_image_to_r2(
    image_url: str,
    slug: str,
    r2_client,
    bucket: str,
    public_url: str,
    dry_run: bool,
    _cache: dict,
) -> Optional[str]:
    """Downloads an image from WordPress and uploads it to R2.
    Returns the new R2 public URL, or None on failure.
    Caches results so each URL is only uploaded once.
    """
    if image_url in _cache:
        return _cache[image_url]

    # Extract filename
    filename = image_url.split("?")[0].split("/")[-1]
    if not filename:
        return None

    r2_key = f"blog/{slug}/{filename}"
    new_url = f"{public_url.rstrip('/')}/blog/{slug}/{filename}"

    if dry_run:
        print(f"    [dry-run] Would upload: {filename} → {r2_key}")
        _cache[image_url] = new_url
        return new_url

    try:
        resp = requests.get(image_url, timeout=30)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        r2_client.put_object(
            Bucket=bucket,
            Key=r2_key,
            Body=resp.content,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
        )
        print(f"    ✓ Uploaded: {filename} → {r2_key}")
        _cache[image_url] = new_url
        return new_url
    except Exception as exc:
        print(f"    ✗ Failed to upload {filename}: {exc}")
        _cache[image_url] = image_url  # keep original URL on failure
        return image_url


def migrate_images(
    markdown: str,
    original_html: str,
    slug: str,
    thumbnail_url: Optional[str],
    r2_client,
    bucket: str,
    public_url: str,
    dry_run: bool,
    cache: dict,
) -> tuple[str, Optional[str]]:
    """
    Finds all image URLs in the Markdown, uploads to R2, replaces URLs.
    Returns (updated_markdown, cover_image_url).
    """
    # Find all image URLs in markdown: ![alt](url) and <img src="url">
    img_pattern = re.compile(
        r'(!\[([^\]]*)\]\()([^)]+)(\))|(<img[^>]+src=["\'])([^"\']+)(["\'][^>]*>)',
        re.IGNORECASE,
    )

    replacements: dict[str, str] = {}

    for match in img_pattern.finditer(markdown):
        url = match.group(3) or match.group(6)
        if url and ("wp-content" in url or url.startswith("http")):
            new_url = upload_image_to_r2(url, slug, r2_client, bucket, public_url, dry_run, cache)
            if new_url and new_url != url:
                replacements[url] = new_url

    for old_url, new_url in replacements.items():
        markdown = markdown.replace(old_url, new_url)

    # Handle cover image
    cover_image: Optional[str] = None
    if thumbnail_url:
        cover_image = upload_image_to_r2(thumbnail_url, slug, r2_client, bucket, public_url, dry_run, cache)

    return markdown, cover_image


# ---------------------------------------------------------------------------
# Frontmatter + file writing
# ---------------------------------------------------------------------------

def make_frontmatter(
    title: str,
    description: str,
    publish_date: str,
    tags: list[str],
    lang: str,
    cover_image: Optional[str] = None,
) -> str:
    lines = [
        "---",
        f"title: {_yaml_str(title)}",
        f"description: {_yaml_str(description)}",
        f"publishDate: {publish_date}",
    ]
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag.lower().replace(' ', '-')}")
    if cover_image:
        lines.append(f"coverImage: {cover_image}")
    lines += [
        f"lang: {lang}",
        "draft: false",
        "---",
    ]
    return "\n".join(lines)


def _yaml_str(value: str) -> str:
    """Wraps a string in double quotes if it contains special YAML characters."""
    needs_quotes = any(c in value for c in ':{}[]|>&*!,#?@`\'"')
    if needs_quotes:
        return '"' + value.replace('"', '\\"') + '"'
    return value


def write_post(out_dir: Path, slug: str, frontmatter: str, body: str, dry_run: bool) -> None:
    out_path = out_dir / f"{slug}.md"
    content = frontmatter + "\n\n" + body + "\n"
    if dry_run:
        print(f"    [dry-run] Would write: {out_path}")
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"    ✓ Written: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate WordPress posts to Astro Markdown + Cloudflare R2"
    )
    parser.add_argument("--xml", required=True, help="Path to WordPress XML export file")
    parser.add_argument("--lang", default="en", choices=["en", "es"], help="Language for all posts (default: en)")
    parser.add_argument("--out-dir", default=None, help="Output directory for .md files (default: src/content/blog-{lang})")

    # R2 config
    parser.add_argument("--r2-account-id", default="", help="Cloudflare account ID")
    parser.add_argument("--r2-access-key", default="", help="R2 access key ID")
    parser.add_argument("--r2-secret-key", default="", help="R2 secret access key")
    parser.add_argument("--r2-bucket", default="alexisalulema-media", help="R2 bucket name")
    parser.add_argument("--r2-public-url", default="https://images.alexisalulema.com", help="Public URL of the R2 bucket")

    parser.add_argument("--dry-run", action="store_true", help="Parse and convert without uploading or writing files")
    parser.add_argument("--skip-images", action="store_true", help="Skip image migration (keep original WordPress URLs)")

    args = parser.parse_args()

    xml_path = Path(args.xml)
    if not xml_path.exists():
        print(f"Error: XML file not found: {xml_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    out_dir = Path(args.out_dir) if args.out_dir else Path(f"src/content/blog-{args.lang}")

    # Set up R2 client
    r2 = None
    if not args.dry_run and not args.skip_images:
        if not all([args.r2_account_id, args.r2_access_key, args.r2_secret_key]):
            print("Error: R2 credentials required unless --dry-run or --skip-images is set.", file=sys.stderr)
            print("  --r2-account-id, --r2-access-key, --r2-secret-key", file=sys.stderr)
            sys.exit(1)
        r2 = _r2_client(args.r2_account_id, args.r2_access_key, args.r2_secret_key)

    print(f"\n{'='*60}")
    print(f"WordPress → Astro Migration")
    print(f"  XML:      {xml_path}")
    print(f"  Language: {args.lang}")
    print(f"  Output:   {out_dir}")
    print(f"  Images:   {'skip' if args.skip_images else ('dry-run' if args.dry_run else f'R2 → {args.r2_bucket}')}")
    print(f"{'='*60}\n")

    # Parse XML
    print("Parsing WordPress XML export...")
    posts, attachments = parse_export(xml_path)
    print(f"Found {len(posts)} published posts, {len(attachments)} attachments.\n")

    image_cache: dict[str, str] = {}
    stats = {"ok": 0, "skipped": 0, "errors": 0}

    for i, post in enumerate(posts, 1):
        title = post["title"]
        slug = post["slug"] or slugify(title)
        raw_date = post["date"]
        content_html = post["content"]
        excerpt = post["excerpt"]
        tags = post["tags"]
        thumbnail_id = post["thumbnail_id"]

        print(f"[{i}/{len(posts)}] {slug}")

        # Parse date
        try:
            publish_date = dateparser.parse(raw_date).strftime("%Y-%m-%d")
        except Exception:
            publish_date = datetime.now().strftime("%Y-%m-%d")
            print(f"  ⚠ Could not parse date '{raw_date}', using today.")

        # Convert HTML → Markdown
        try:
            body = html_to_markdown(content_html)
        except Exception as exc:
            print(f"  ✗ Markdown conversion failed: {exc}")
            stats["errors"] += 1
            continue

        description = make_description(excerpt, content_html)

        # Resolve thumbnail URL
        thumbnail_url: Optional[str] = None
        if thumbnail_id and thumbnail_id in attachments:
            thumbnail_url = attachments[thumbnail_id]

        # Migrate images
        cover_image: Optional[str] = None
        if not args.skip_images and (r2 or args.dry_run):
            try:
                body, cover_image = migrate_images(
                    markdown=body,
                    original_html=content_html,
                    slug=slug,
                    thumbnail_url=thumbnail_url,
                    r2_client=r2,
                    bucket=args.r2_bucket,
                    public_url=args.r2_public_url,
                    dry_run=args.dry_run,
                    cache=image_cache,
                )
            except Exception as exc:
                print(f"  ⚠ Image migration error (keeping original URLs): {exc}")
        elif thumbnail_url:
            cover_image = thumbnail_url  # keep original if skipping

        # Build frontmatter
        frontmatter = make_frontmatter(
            title=title,
            description=description,
            publish_date=publish_date,
            tags=tags,
            lang=args.lang,
            cover_image=cover_image,
        )

        # Write file
        try:
            write_post(out_dir, slug, frontmatter, body, args.dry_run)
            stats["ok"] += 1
        except Exception as exc:
            print(f"  ✗ Could not write file: {exc}")
            stats["errors"] += 1

        # Small delay to avoid hammering WordPress server
        if not args.dry_run and not args.skip_images and i < len(posts):
            time.sleep(0.2)

    print(f"\n{'='*60}")
    print(f"Migration complete.")
    print(f"  ✓ {stats['ok']} posts migrated")
    if stats["errors"]:
        print(f"  ✗ {stats['errors']} errors")
    if stats["skipped"]:
        print(f"  – {stats['skipped']} skipped")
    print(f"{'='*60}\n")

    if stats["ok"] > 0 and not args.dry_run:
        print(f"Next steps:")
        print(f"  1. Review the generated .md files in {out_dir}/")
        print(f"  2. Check descriptions (auto-generated from excerpt/content)")
        print(f"  3. Run: npm run dev  →  verify posts appear correctly")
        print(f"  4. Commit: git add {out_dir}/ && git commit -m 'feat: import WordPress posts'")


if __name__ == "__main__":
    main()
