import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blogSchema = z.object({
  title: z.string(),
  description: z.string(),
  publishDate: z.coerce.date(),
  updatedDate: z.coerce.date().optional(),
  tags: z.array(z.string()).default([]),
  coverImage: z.string().optional(),
  draft: z.boolean().default(false),
  lang: z.enum(['en', 'es']),
});

const blogEn = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog-en' }),
  schema: blogSchema,
});

const blogEs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog-es' }),
  schema: blogSchema,
});

export const collections = {
  'blog-en': blogEn,
  'blog-es': blogEs,
};
