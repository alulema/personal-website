import { en } from './en';
import { es } from './es';

export const languages = { en, es } as const;
export type Locale = keyof typeof languages;

export function useTranslations(locale: Locale) {
  return languages[locale];
}

export function getAlternateLocale(locale: Locale): Locale {
  return locale === 'en' ? 'es' : 'en';
}

export function getLocalePath(locale: Locale, path: string): string {
  if (locale === 'en') return path;
  return `/es${path}`;
}
