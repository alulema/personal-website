# Bitácora de desarrollo — alexisalulema.com

Registro cronológico de decisiones, avances y cambios durante el rediseño del sitio personal.

---

## Contexto inicial (2026-04-03)

**Situación de partida:** Sitio en WordPress sobre AWS Lightsail (`alexisalulema.com`). Blog técnico ("The Code-It List") con posts sobre Python, ML, arquitecturas y herramientas. Diseño genérico de WordPress, sin personalización, sin identidad diferenciada.

**Motivación del rediseño:**
- WordPress demasiado pesado y costoso para un blog personal
- Sin control sobre el diseño ni la experiencia
- Imposible mostrar demos interactivos de experimentos de IA/ML
- Formulario de contacto generaba spam excesivo
- Stack no alineado con el perfil técnico actual (Microsoft, ML, Azure)

---

## Fase 1 — Setup base (2026-04-03)

### Decisiones de stack

| Decisión | Alternativas consideradas | Por qué se eligió |
|---|---|---|
| **Astro** como framework | Next.js, SvelteKit, Hugo | SSG puro, mejor performance, i18n nativo, ideal para blogs |
| **Tailwind CSS 4** | CSS modules, styled-components | Responsivo rápido, design tokens con CSS variables |
| **Azure Static Web Apps** | Vercel, Netlify, GitHub Pages | Cuenta Azure corporativa disponible, free tier generoso |
| **FastAPI** para backend | Django, Flask, Node.js | Ligero, async nativo, documentación automática, experiencia previa |
| **Cloudflare** para DNS | Azure DNS | Free tier, Turnstile anti-spam, R2 para imágenes |

### Lo construido

- Proyecto Astro 6 con TypeScript strict
- Tailwind CSS 4 integrado vía plugin Vite
- Sistema de i18n: EN (default, sin prefijo) + ES (`/es/*`)
- Sistema de temas dark/light:
  - Dark por defecto
  - Script inline en `<head>` previene flash al cargar
  - Toggle persistido en `localStorage`
  - CSS custom properties (variables) como design tokens
- Header responsivo con menú hamburguesa en móvil
- Footer con links a GitHub y LinkedIn
- Componentes `ThemeToggle` y `LangToggle`
- Hero page bilingüe con gradiente en el título
- 18 páginas stub bilingües (estructura completa del sitio)
- Estructura de carpetas: `src/` (frontend), `api/` (FastAPI), `infrastructure/` (Bicep)

### Problemas encontrados

- **Astro 6 removió `output: "hybrid"`**: Ahora `output: "static"` cubre ambos casos. Se actualizó el config.
- **CLI interactivo de Astro**: No funciona en modo no-interactivo. Se configuró manualmente.

---

## Fase 2 — Blog + CMS (2026-04-03)

### Decisiones

| Decisión | Por qué |
|---|---|
| **Keystatic** como CMS | Git-based, no requiere base de datos, editor visual tipo Notion, gratis |
| **Markdown/Markdoc** para posts | Portabilidad, control de versiones, soporte nativo en Astro |
| Keystatic **solo en dev** | En producción el admin no existe → cero superficie de ataque. Build de producción excluye Keystatic via `isProduction` check |
| **Cloudflare R2** para imágenes | Egress gratuito vs Azure Blob Storage que cobra por descarga |
| **Modo local** de Keystatic (por ahora) | En Fase 7 se migra a GitHub mode + Microsoft Entra ID auth |

### Lo construido

- Content Collections (Astro 6 con loaders glob):
  - `blog-en`: posts en inglés en `src/content/blog-en/`
  - `blog-es`: posts en español en `src/content/blog-es/`
  - Schema: `title`, `description`, `publishDate`, `updatedDate`, `tags`, `coverImage`, `draft`, `lang`
- Keystatic config (`keystatic.config.ts`) con colecciones para EN y ES
- Páginas del blog:
  - `/blog` y `/es/blog`: grid de posts, filtro por draft
  - `/blog/[slug]` y `/es/blog/[slug]`: post individual con prose styles completos
- Componente `BlogCard`: imagen lazy, fecha por locale, tiempo de lectura estimado, tags
- Utilidad `getReadingTime` (200 wpm)
- Post de prueba en inglés y español (sobre asyncio en Python)

### Problemas encontrados

- **Keystatic no soporta Astro 6 en peer deps**: Resuelto con `--legacy-peer-deps`. Funciona correctamente.
- **Keystatic requiere React**: Se instaló `@astrojs/react` + `react` + `react-dom`.
- **Content config movida en Astro 6**: De `src/content/config.ts` a `src/content.config.ts` con loaders. Se migró.
- **`post.slug` removido en Astro 6**: Ahora se usa `post.id` (nombre del archivo sin extensión).
- **Directorio `.astro/` faltante**: Causaba error `ENOENT` al iniciar dev server. Creado manualmente.

---

## Fase 3 — Galería de proyectos (2026-04-04)

### Decisiones

| Decisión | Por qué |
|---|---|
| **Datos en TypeScript** (`src/data/projects.ts`) | Proyectos son datos estructurados, no contenido largo. TypeScript da type-safety sin overhead de colecciones |
| **Status dinámico** via fetch al cliente | El sitio es estático; el status (offline/pending/active) se consulta en runtime desde la API |
| **React solo para el modal** | El resto de la galería es Astro puro. React solo donde hay interactividad compleja (formulario con estado) |
| **`CustomEvent`** para comunicación Astro↔React | Desacoplamiento limpio entre el botón Astro y el modal React |

### Lo construido

- `src/data/projects.ts`: 4 proyectos reales con datos bilingües
  - RAG Chatbot (Azure AI Search + LangChain)
  - BERT Text Classifier (PyTorch + Transformers)
  - Multi-Agent AI (LangGraph + Semantic Kernel)
  - FastAPI Production Patterns
- Componente `ProjectCard.astro`:
  - Badge de status con dot animado (verde/amarillo/gris)
  - Countdown timer cuando demo está activo
  - Botón "Request Access" / "Open Demo" según estado
  - Fetch automático desde `/api/demo/status/{id}` con fallback silencioso
- `DemoRequestModal.tsx` (React):
  - Nombre, email, motivo (opcional)
  - Estados: idle → submitting → success/error
  - Cierra con Escape o clic fuera del panel
  - Bilingüe EN/ES
  - Llama a `POST /api/demo/request` (API en Fase 7)
- Páginas `/projects` y `/es/projects`:
  - Grid responsivo
  - Filtros por categoría (All / AI & LLM / ML / Backend)
  - Status fetch automático al cargar

### Sistema de demos on-demand (diseñado, pendiente de implementar)

El backend se construye en Fase 7. El flujo diseñado:
1. Usuario solicita acceso → email al admin con botones de aprobación
2. Admin aprueba con duración (30min/1h/2h)
3. Azure Function genera JWT + escala Container App a 1 réplica
4. Usuario recibe email con link de acceso
5. Timer trigger limpia sesiones expiradas + escala Container Apps a 0

---

## Git y control de versiones (2026-04-04)

### Problemas encontrados al configurar el repo

- **Nombre de repo con guión inicial** (`-alexisalulema.com`): GitHub lo creó con nombre problemático. Se resolvió creando un nuevo repo `personal-website`.
- **Conflicto Git Credential Manager**: WSL usaba credenciales de Windows que sobreescribían las de `gh`. Se resolvió configurando SSH.
- **SSH key no automática**: La clave generada como `~/.ssh/github` (no nombre por defecto) requirió crear `~/.ssh/config` con `IdentityFile`.
- **Token PAT expuesto en chat**: El token fue revelado accidentalmente. Se revocó inmediatamente en GitHub.

### Configuración final

```
Protocolo: SSH
Repo: github.com/alulema/personal-website
Branch: main
SSH key: ~/.ssh/github (con config entry en ~/.ssh/config)
```

---

## Fase 4 — Páginas de contenido (2026-04-05)

### Lo construido

**About** (`/about`, `/es/about`)
- Bio con roles actuales (Microsoft + UOC) en narrativa cohesiva
- Stats visuales: 15+ años, 2 roles actuales, 1 paper publicado, 7+ certificaciones
- Skills agrupados en 5 categorías con badges (Languages, AI/ML, Cloud, Databases, DevOps)
- Timeline de experiencia laboral con marcador visual
- Educación: UNM (MS IoT) + ESPE (B.S. Electronics)

**Research** (`/research`, `/es/research`)
- Paper Springer Q3 como feature card con border-left accent
- "Deep Learning Methods in NLP" — ICAT 2019, Quito
- Badges de tech stack + sección de intereses de investigación

**Teaching** (`/teaching`, `/es/teaching`)
- Rol en UOC como Profesor Colaborador (2025–presente)
- Filosofía de enseñanza (industria + academia)
- Credenciales académicas

**Certifications** (`/certifications`, `/es/certifications`)
- 7 certificaciones en grid responsivo 3 columnas
- Border-left de color por issuer: Microsoft (azul), AWS (naranja), GitHub (verde), Databricks (rojo), Coursera (azul)
- GitHub Copilot (Jan 2026), Azure x3 (2025), Databricks LLM (Jan 2024), GenAI Coursera (Nov 2023), AWS CCP (Jul 2022)

**Uses** (`/uses`, `/es/uses`)
- Stack diario: VS Code + Claude Code, WSL2, GitHub CLI
- Lenguajes, cloud (Azure + AWS), AI/ML stack completo, bases de datos

**Now** (`/now`, `/es/now`)
- Actualizado a Abril 2026
- Microsoft (Databricks/Fabric + Hackathon 2025) + UOC + rediseño del sitio + LLMOps

---

## Fase 5 — Contacto + Cloudflare Turnstile (2026-04-05)

### Lo construido

**Contact** (`/contact`, `/es/contact`)
- Layout dos columnas: info/social izquierda, formulario derecha
- Campos: nombre, email, asunto, mensaje
- **Cloudflare Turnstile** integrado como widget anti-spam
  - Clave de prueba `1x00000000000000000000AA` activa en dev
  - Clave real se configura via `PUBLIC_TURNSTILE_SITE_KEY` en `.env`
  - El widget valida en el cliente; la clave secreta se verifica en la Azure Function (Fase 7)
- Feedback inline: éxito (verde) / error (rojo)
- Reset automático del widget Turnstile tras envío exitoso
- Dirección de email nunca expuesta en el HTML
- `.env.example` creado con todas las variables de entorno necesarias

### Variables de entorno requeridas

| Variable | Descripción | Dónde obtenerla |
|---|---|---|
| `PUBLIC_TURNSTILE_SITE_KEY` | Clave pública del widget | Cloudflare Dashboard → Turnstile |
| `TURNSTILE_SECRET_KEY` | Clave secreta para verificar tokens | Cloudflare Dashboard → Turnstile |
| `CONTACT_DESTINATION_EMAIL` | Email destino de mensajes | Hardcoded: contact@alexisalulema.com |
| `AZURE_COMMUNICATION_CONNECTION_STRING` | Para envío de emails | Azure Portal → Communication Services |
| `JWT_SECRET` | Firma de tokens de demo on-demand | Generar aleatoriamente (min 32 chars) |
| `AZURE_STORAGE_CONNECTION_STRING` | Tabla de tickets de demo | Azure Portal → Storage Account |

---

## Checklist para ir a producción

### Antes del primer deploy

- [ ] **Cloudflare Turnstile**: Crear sitio en [dash.cloudflare.com](https://dash.cloudflare.com) → Turnstile → Add site. Agregar `alexisalulema.com` como dominio. Copiar Site Key y Secret Key.
- [ ] **Azure Communication Services**: Crear recurso en Azure Portal. Obtener connection string. Verificar dominio sender.
- [ ] **Azure Storage Account**: Crear cuenta de almacenamiento. Obtener connection string para Table Storage.
- [ ] **Variables de entorno en Azure Static Web Apps**: En Azure Portal → Static Web App → Configuration → Application settings, agregar todas las variables del `.env.example`.
- [ ] **Cloudflare DNS**: Apuntar `alexisalulema.com` a Azure Static Web Apps. Agregar registros CNAME para subdominios de demos.
- [ ] **Custom domain en Azure Static Web Apps**: Agregar `alexisalulema.com` y habilitar SSL automático.
- [ ] **Cloudflare R2**: Crear bucket `alexisalulema-media`. Configurar dominio custom `images.alexisalulema.com`.
- [ ] **Microsoft Clarity**: Crear proyecto en [clarity.microsoft.com](https://clarity.microsoft.com). Agregar snippet en `BaseLayout.astro`.
- [ ] **Reemplazar links placeholder**: Paper de Springer (href="#" en research.astro), links de certificaciones.

### Keystatic en producción (Fase 8)

- [ ] Cambiar `keystatic.config.ts` de `kind: 'local'` a `kind: 'github'`
- [ ] Crear OAuth App en GitHub → Settings → Developer settings
- [ ] Configurar `staticwebapp.config.json` con protección de rutas `/keystatic*`
- [ ] Asignar rol `admin` a `contact@alexisalulema.com` en la config de Azure Static Web Apps

### Post-deploy

- [ ] Verificar sitemap en `alexisalulema.com/sitemap-index.xml` (generado automáticamente en build)
- [ ] Verificar `robots.txt` (en `public/robots.txt`, ya listo)
- [ ] Probar formulario de contacto end-to-end
- [ ] Probar flujo completo de solicitud de demo
- [ ] Verificar toggle dark/light en móvil
- [ ] Verificar navegación EN ↔ ES
- [ ] Verificar que `/keystatic` devuelve 404 en producción (Keystatic excluido del build)

---

## Fase 6 — SEO (2026-04-03)

### Decisiones

| Decisión | Por qué |
|---|---|
| **`@astrojs/sitemap`** con filtro | Genera `sitemap-index.xml` automáticamente en build. Filtro excluye rutas `/keystatic` |
| **hreflang dinámico** en BaseLayout | Se calcula la URL alternativa desde `Astro.url.pathname` — funciona para todas las páginas sin configuración extra |
| **OG image SVG** (`og-default.svg`) | Generado en SVG para tener un fallback inmediato. Reemplazable por PNG real cuando el sitio esté en producción |
| **`robots.txt`** con `Disallow: /keystatic/` | Belt-and-suspenders aunque Keystatic ya está excluido del build de producción |

### Lo construido

- `@astrojs/sitemap` instalado (`--legacy-peer-deps`) y configurado en `astro.config.mjs`
  - Filtro para excluir rutas `/keystatic`
  - Genera `sitemap-index.xml` + `sitemap-0.xml` con las 22 páginas del sitio (EN + ES)
- `public/robots.txt`: `Allow: /`, `Disallow: /keystatic/`, apunta al sitemap
- `hreflang` en `BaseLayout.astro`: `<link rel="alternate">` para EN, ES y `x-default`
  - URL calculada dinámicamente desde `Astro.url.pathname`
- `public/images/og-default.svg`: imagen OG branded (1200×630) con nombre, tagline y colores del sitio
- `BaseLayout.astro` actualizado: `ogImage` default apunta a `/images/og-default.svg`

### Problemas encontrados

- **`@astrojs/sitemap` peer deps conflict con Astro 6**: Resuelto con `--legacy-peer-deps` (patrón recurrente).

---

## Pendiente (próximas fases)

| Fase | Contenido |
|---|---|
| ~~**6**~~ | ~~SEO: sitemap, robots.txt, Open Graph images, hreflang~~ ✓ |
| **7** | Backend FastAPI: demo on-demand + formulario de contacto (Azure Functions) |
| **8** | Autenticación: Microsoft Entra ID para Keystatic admin en producción |
| **9** | Deploy: Azure Static Web Apps + CI/CD GitHub Actions + headers de seguridad |
| **Migración** | Importar posts del blog actual de WordPress |

---

## Notas de arquitectura

- **Keystatic en producción** (Fase 8): Se migrará a GitHub mode. El admin estará en `alexisalulema.com/keystatic`, protegido por Azure Static Web Apps con Microsoft Entra ID. Solo `contact@alexisalulema.com` tiene acceso.
- **AdSense**: La arquitectura está lista. Cuando el sitio migre a cuenta personal, solo hay que agregar el script de AdSense en `BaseLayout.astro`.
- **Microsoft Clarity**: Pendiente de agregar el snippet en `BaseLayout.astro` cuando el sitio esté en producción.
