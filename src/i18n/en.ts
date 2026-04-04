export const en = {
  // Navigation
  nav: {
    home: 'Home',
    about: 'About',
    blog: 'Blog',
    projects: 'Projects',
    research: 'Research',
    teaching: 'Teaching',
    certifications: 'Certifications',
    uses: 'Uses',
    now: 'Now',
    contact: 'Contact',
  },
  // Hero
  hero: {
    title: 'Alexis Alulema',
    roles: 'Software Engineer · ML Specialist · Educator',
    description:
      'Building AI systems at Microsoft. Teaching at Universitat Oberta de Catalunya. 15+ years turning complex problems into scalable solutions.',
    cta_blog: 'Read the blog',
    cta_projects: 'View projects',
  },
  // Theme toggle
  theme: {
    toggle_light: 'Switch to light mode',
    toggle_dark: 'Switch to dark mode',
  },
  // Language toggle
  lang: {
    switch: 'Español',
  },
  // Blog
  blog: {
    title: 'Blog',
    subtitle: 'Notes on software development, machine learning, and engineering.',
    read_more: 'Read more',
    min_read: 'min read',
  },
  // Projects
  projects: {
    title: 'Projects',
    subtitle: 'Experiments and demos built with real technology.',
    request_access: 'Request Access',
    active: 'Active',
    offline: 'Offline',
    pending: 'Pending approval',
    tech_stack: 'Tech stack',
  },
  // Research
  research: {
    title: 'Research',
    subtitle: 'Published academic work and conference presentations.',
  },
  // Teaching
  teaching: {
    title: 'Teaching',
    subtitle: 'Academic collaboration and knowledge sharing.',
  },
  // Certifications
  certifications: {
    title: 'Certifications',
    subtitle: 'Professional credentials and continuous learning.',
  },
  // Uses
  uses: {
    title: 'Uses',
    subtitle: 'My hardware, software, and tools.',
  },
  // Now
  now: {
    title: 'Now',
    subtitle: "What I'm currently focused on.",
    updated: 'Last updated',
  },
  // Contact
  contact: {
    title: 'Contact',
    subtitle: "Let's connect.",
    name: 'Name',
    email: 'Email',
    message: 'Message',
    send: 'Send message',
    success: 'Message sent successfully.',
    error: 'Something went wrong. Please try again.',
  },
  // Footer
  footer: {
    built_with: 'Built with',
    source: 'Source',
  },
  // 404
  not_found: {
    title: 'Page not found',
    back: 'Back to home',
  },
} as const;

export type TranslationKey = typeof en;
