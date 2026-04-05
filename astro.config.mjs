// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';
import keystatic from '@keystatic/astro';
import sitemap from '@astrojs/sitemap';

const isProduction = process.env.NODE_ENV === 'production';

// In production, include Keystatic only when GitHub OAuth is configured.
// In dev, always include Keystatic (local mode, no OAuth needed).
const useKeystatic = !isProduction || !!process.env.KEYSTATIC_GITHUB_CLIENT_ID;

// https://astro.build/config
export default defineConfig({
  site: 'https://alexisalulema.com',
  output: 'static',
  integrations: useKeystatic
    ? [react(), keystatic(), sitemap({ filter: (page) => !page.includes('/keystatic') })]
    : [react(), sitemap({ filter: (page) => !page.includes('/keystatic') })],
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