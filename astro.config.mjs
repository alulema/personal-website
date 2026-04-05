// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';
import keystatic from '@keystatic/astro';
import sitemap from '@astrojs/sitemap';

const isProduction = process.env.NODE_ENV === 'production';

// https://astro.build/config
export default defineConfig({
  site: 'https://alexisalulema.com',
  output: 'static',
  // Keystatic admin is local-only — excluded from production builds
  integrations: isProduction
    ? [react(), sitemap({ filter: (page) => !page.includes('/keystatic') })]
    : [react(), keystatic(), sitemap({ filter: (page) => !page.includes('/keystatic') })],
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
});