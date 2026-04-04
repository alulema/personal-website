import { config, collection, fields } from '@keystatic/core';

const blogFields = {
  title: fields.text({ label: 'Title', validation: { isRequired: true } }),
  description: fields.text({
    label: 'Description',
    multiline: true,
    validation: { isRequired: true },
  }),
  publishDate: fields.date({
    label: 'Publish Date',
    validation: { isRequired: true },
  }),
  updatedDate: fields.date({ label: 'Updated Date' }),
  tags: fields.array(fields.text({ label: 'Tag' }), {
    label: 'Tags',
    itemLabel: (props) => props.fields.value.value || 'Tag',
  }),
  coverImage: fields.text({
    label: 'Cover Image URL',
    description: 'Full URL from Cloudflare R2 (e.g. https://images.alexisalulema.com/blog/...)',
  }),
  draft: fields.checkbox({ label: 'Draft', defaultValue: false }),
};

export default config({
  storage: { kind: 'local' },

  collections: {
    'blog-en': collection({
      label: 'Blog Posts (English)',
      slugField: 'title',
      path: 'src/content/blog-en/*',
      format: { contentField: 'content' },
      entryLayout: 'content',
      schema: {
        ...blogFields,
        lang: fields.select({
          label: 'Language',
          options: [{ label: 'English', value: 'en' }],
          defaultValue: 'en',
        }),
        content: fields.markdoc({
          label: 'Content',
          options: {
            bold: true,
            italic: true,
            strikethrough: true,
            code: true,
            heading: [1, 2, 3, 4],
            blockquote: true,
            orderedList: true,
            unorderedList: true,
            table: true,
            link: true,
            image: true,
          },
        }),
      },
    }),

    'blog-es': collection({
      label: 'Blog Posts (Español)',
      slugField: 'title',
      path: 'src/content/blog-es/*',
      format: { contentField: 'content' },
      entryLayout: 'content',
      schema: {
        ...blogFields,
        lang: fields.select({
          label: 'Idioma',
          options: [{ label: 'Español', value: 'es' }],
          defaultValue: 'es',
        }),
        content: fields.markdoc({
          label: 'Contenido',
          options: {
            bold: true,
            italic: true,
            strikethrough: true,
            code: true,
            heading: [1, 2, 3, 4],
            blockquote: true,
            orderedList: true,
            unorderedList: true,
            table: true,
            link: true,
            image: true,
          },
        }),
      },
    }),
  },
});
