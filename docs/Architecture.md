# Architecture — alexisalulema.com

## Visión general

Sitio web personal con blog técnico, galería de proyectos/demos con activación bajo demanda, y formulario de contacto anti-spam. Diseñado para operar con costo mínimo ($0–3/mes) sobre infraestructura Azure de cuenta corporativa, con capacidad de monetización futura (AdSense) al migrar a cuenta personal.

---

## Stack tecnológico

| Capa | Tecnología | Justificación |
|---|---|---|
| Frontend | **Astro 6** + TypeScript | SSG, performance excelente, i18n nativo, Content Collections |
| Estilos | **Tailwind CSS 4** + CSS custom properties | Diseño responsivo, sistema de tokens intercambiable |
| CMS | **Keystatic** (local mode en dev) | Editor visual Git-based, sin base de datos, gratuito |
| Blog content | **Markdown / Markdoc** | Portabilidad total, control de versiones con Git |
| Backend APIs | **FastAPI** (Python) | Ligero, async nativo, documentación automática (Swagger) |
| Hosting frontend | **Azure Static Web Apps** | Free tier, CDN incluida, CI/CD con GitHub |
| Hosting API | **Azure Functions** (Python) | Serverless, cobro por uso, $0 en idle |
| Demos/experimentos | **Azure Container Apps** | Scale-to-zero, un subdominio por demo |
| Imágenes del blog | **Cloudflare R2** | Egress gratuito, CDN de Cloudflare incluida |
| DNS / Proxy | **Cloudflare** | Free tier, analytics, Turnstile anti-spam |
| Monitoreo | **Microsoft Clarity** + **Cloudflare Analytics** | Gratuitos, sin cookies invasivas |

---

## Diagrama de arquitectura

```
                        Cloudflare (DNS + CDN)
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    alexisalulema.com    images.alexisalulema.com   *.alexisalulema.com
              │                │                │
    Azure Static         Cloudflare R2      Azure Container Apps
    Web Apps             (imágenes blog)    (demos individuales)
    (Astro SSG)                │                │
              │           blog posts        demo backends
              │           screenshots       (FastAPI/Python)
              │
    Azure Functions (Python/FastAPI)
    ├── POST /api/demo/request      ← solicitud de acceso
    ├── GET  /api/demo/approve/{t}  ← aprobación por email
    ├── GET  /api/demo/status/{id}  ← estado del demo
    ├── POST /api/contact           ← formulario de contacto
    └── Timer: cleanup sesiones expiradas
              │
    Azure Table Storage
    └── DemoRequests (id, email, status, expires_at, jwt)
```

---

## Estructura de carpetas

```
PersonalWebSite/
├── src/                          # Frontend Astro
│   ├── components/               # Componentes reutilizables
│   │   ├── ui/                   # Primitivos (ThemeToggle, LangToggle)
│   │   ├── BlogCard.astro
│   │   ├── ProjectCard.astro
│   │   ├── DemoRequestModal.tsx  # React (interactivo)
│   │   ├── Header.astro
│   │   └── Footer.astro
│   ├── content/                  # Contenido del blog (Markdown)
│   │   ├── blog-en/              # Posts en inglés
│   │   └── blog-es/              # Posts en español
│   ├── data/
│   │   └── projects.ts           # Datos estructurados de proyectos
│   ├── i18n/
│   │   ├── en.ts                 # Traducciones inglés
│   │   ├── es.ts                 # Traducciones español
│   │   └── index.ts              # Helpers (useTranslations, getLocalePath)
│   ├── layouts/
│   │   └── BaseLayout.astro      # Layout base con SEO, fonts, scripts
│   ├── pages/
│   │   ├── index.astro           # Homepage EN (/)
│   │   ├── blog.astro            # Lista posts EN
│   │   ├── blog/[slug].astro     # Post individual EN
│   │   ├── projects.astro        # Galería EN
│   │   ├── about.astro
│   │   ├── research.astro
│   │   ├── teaching.astro
│   │   ├── certifications.astro
│   │   ├── uses.astro
│   │   ├── now.astro
│   │   ├── contact.astro
│   │   └── es/                   # Espejo en español (/es/*)
│   ├── styles/
│   │   └── global.css            # Design tokens + estilos base
│   └── utils/
│       └── reading-time.ts       # Utilidad: tiempo estimado de lectura
│
├── api/                          # Backend FastAPI (Azure Functions)
│   ├── demo_manager/             # Gestión de tickets de demo
│   └── contact/                  # Formulario de contacto
│
├── infrastructure/               # Azure Bicep (IaC)
│
├── docs/                         # Documentación del proyecto
│   ├── Design.md
│   ├── Architecture.md
│   └── Devlog.md
│
├── .github/
│   └── workflows/                # CI/CD pipelines
│
├── astro.config.mjs
├── keystatic.config.ts
├── src/content.config.ts         # Astro Content Collections (Astro 6)
├── package.json
└── tsconfig.json
```

---

## Routing i18n

| Ruta EN | Ruta ES | Descripción |
|---|---|---|
| `/` | `/es/` | Homepage |
| `/blog` | `/es/blog` | Lista de posts |
| `/blog/[slug]` | `/es/blog/[slug]` | Post individual |
| `/projects` | `/es/projects` | Galería de demos |
| `/about` | `/es/about` | Sobre mí |
| `/research` | `/es/research` | Investigación/paper |
| `/teaching` | `/es/teaching` | Docencia en UOC |
| `/certifications` | `/es/certifications` | Certificaciones |
| `/uses` | `/es/uses` | Herramientas |
| `/now` | `/es/now` | Qué hago ahora |
| `/contact` | `/es/contact` | Contacto |

El inglés es el idioma por defecto (`prefixDefaultLocale: false`). Las rutas en español tienen prefijo `/es/`.

---

## Content Collections (Astro 6)

Definidas en `src/content.config.ts` con loaders glob:

```typescript
const blogEn = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog-en' }),
  schema: blogSchema,  // title, description, publishDate, tags, coverImage, draft, lang
});
```

Los posts en draft (`draft: true`) se excluyen del build de producción. El `id` del post es el nombre del archivo sin extensión.

---

## Sistema de demos on-demand

### Flujo de activación

```
1. Usuario → "Request Access" en galería
2. Modal React → POST /api/demo/request { projectId, name, email, reason }
3. Azure Function → crea ticket en Table Storage (status: pending)
4. Azure Function → envía email al admin con botones [Approve 30m] [Approve 1h] [Deny]
5. Admin aprueba → GET /api/demo/approve/{token}?duration=60
6. Azure Function → genera JWT firmado (expiresAt = now + duration)
7. Azure Function → escala Container App a 1 réplica (Azure SDK)
8. Azure Function → envía email al usuario con link de acceso
9. Usuario accede al demo → Container App valida JWT en middleware
10. Timer trigger (cada 5min) → limpia sesiones expiradas + escala a 0
```

### Seguridad

- JWT firmado con clave secreta (Azure Key Vault en producción)
- El email del admin nunca aparece en el HTML público
- Rate limiting por IP en la Azure Function de solicitudes
- Cloudflare Turnstile en el formulario de solicitud

---

## Autenticación (Keystatic admin)

- **Ambiente de desarrollo**: Keystatic corre en modo local (`localhost:4321/keystatic`), sin autenticación
- **Producción** (Fase 7): Azure Static Web Apps + Microsoft Entra ID
  - Ruta `/keystatic/*` protegida en `staticwebapp.config.json`
  - Solo `contact@alexisalulema.com` tiene rol `admin`
  - Login con cuenta Microsoft + MFA via Microsoft Authenticator
  - Keystatic en modo GitHub: commits directos al repo → auto-deploy

---

## CI/CD

```
Push a main
  → GitHub Actions
  → npx astro build (NODE_ENV=production)
  → Deploy a Azure Static Web Apps
  → ~2 minutos hasta producción
```

---

## SEO

- `<meta name="robots" content="index, follow">`
- Sin meta `generator` (no revela Astro)
- Headers de Azure Static Web Apps: sin `X-Powered-By`
- Sitemap automático (`/sitemap-index.xml`)
- Open Graph completo en cada página
- URLs canónicas configuradas
- `hreflang` entre versiones EN/ES

---

## Monitoreo

| Herramienta | Qué mide | Costo |
|---|---|---|
| Cloudflare Analytics | Tráfico, países, bandwidth, bots | Gratis |
| Microsoft Clarity | Heatmaps, session recordings, funnels | Gratis |

Sin Google Analytics — mejor privacidad para visitantes europeos (GDPR).

---

## Costos estimados

| Servicio | Tier | Costo/mes |
|---|---|---|
| Azure Static Web Apps | Free | $0 |
| Azure Functions | Consumption (1M free) | ~$0 |
| Azure Container Apps | Scale-to-zero | $0–3 |
| Azure Table Storage | <1GB | ~$0 |
| Cloudflare R2 | Free (10GB) | $0 |
| Cloudflare DNS/Turnstile | Free | $0 |
| **Total** | | **$0–3** |
