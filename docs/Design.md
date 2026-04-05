# Design System — alexisalulema.com

## Principios de diseño

1. **Contenido primero** — El diseño no compite con el contenido técnico. La tipografía y el espacio hacen el trabajo.
2. **Dark mode por defecto** — La audiencia principal son desarrolladores. El modo oscuro es el estándar.
3. **Intercambiable** — El sistema de tokens CSS permite cambiar el tema visual completo modificando solo las variables en `global.css`.
4. **Sin stack fingerprinting** — Ningún elemento visual revela la tecnología subyacente (sin meta `generator`, sin headers `X-Powered-By`).

---

## Paleta de colores

### Tokens CSS (`src/styles/global.css`)

| Token | Dark (default) | Light |
|---|---|---|
| `--color-bg` | `#0a0f1e` | `#f8fafc` |
| `--color-bg-secondary` | `#111827` | `#f1f5f9` |
| `--color-bg-card` | `#0f172a` | `#ffffff` |
| `--color-border` | `rgba(255,255,255,0.08)` | `rgba(0,0,0,0.08)` |
| `--color-text` | `#e2e8f0` | `#0f172a` |
| `--color-text-muted` | `#94a3b8` | `#64748b` |
| `--color-accent` | `#38bdf8` | `#0284c7` |
| `--color-accent-hover` | `#7dd3fc` | `#0369a1` |
| `--color-accent-2` | `#818cf8` | `#4f46e5` |

### Criterio de elección

- **Fondo azul marino profundo** (`#0a0f1e`) en lugar de negro puro — reduce la fatiga visual y da profundidad.
- **Acento sky-400** (`#38bdf8`) — evoca datos, IA, tecnología sin ser cliché. Contraste adecuado sobre fondo oscuro (WCAG AA).
- **Acento índigo** (`#818cf8`) — complementario para gradientes y elementos secundarios.

---

## Tipografía

| Rol | Fuente | Uso |
|---|---|---|
| Texto UI | **Inter** (400, 500, 600, 700) | Cuerpo, navegación, botones |
| Código / mono | **JetBrains Mono** (400, 500) | Snippets, badges, fechas, metadatos |

Cargadas desde Google Fonts con `display=swap` para evitar FOIT. Preconnect activado.

### Escala tipográfica

- Hero title: `clamp(2.5rem, 6vw, 4.5rem)` — fluido entre móvil y desktop
- Título de página: `clamp(2rem, 5vw, 3rem)`
- Título de post: `clamp(1.75rem, 4vw, 2.75rem)`
- Cuerpo de post: `1.0625rem` / `line-height: 1.8`

---

## Sistema de temas

El toggle dark/light funciona mediante el atributo `data-theme` en el elemento `<html>`:

```html
<html data-theme="dark">   <!-- dark (default) -->
<html data-theme="light">  <!-- light -->
```

El estado se persiste en `localStorage` bajo la clave `theme`. Un script inline en `<head>` (antes del paint) previene el flash de tema incorrecto:

```js
const stored = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.setAttribute('data-theme', stored || (prefersDark ? 'dark' : 'light'));
```

---

## Componentes base

### Card

```css
.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: border-color 150ms, transform 150ms;
}
.card:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
}
```

### Badge

Usado para tags, tech stack, metadatos:
```css
.badge {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-muted);
}
```

### Botones

| Variante | Uso |
|---|---|
| `.btn-primary` | CTA principal (fondo `--color-accent`) |
| `.btn-secondary` | Acciones secundarias (borde, sin fondo) |
| `.btn-request` | Solicitar acceso a demo (borde accent, sin fondo) |
| `.btn-open-demo` | Demo activo (fondo verde `#4ade80`) |

---

## Status indicators (galería de demos)

| Estado | Color | Descripción |
|---|---|---|
| `active` | `#4ade80` (verde) con glow | Container App corriendo |
| `pending` | `#fbbf24` (amarillo) | Solicitud enviada, pendiente de aprobación |
| `offline` | `--color-text-muted` (gris) | Container App en 0 réplicas |

---

## Layout responsivo

Breakpoints implícitos con CSS moderno (sin media queries explícitos donde sea posible):

```css
/* Grid de cards — se ajusta solo */
grid-template-columns: repeat(auto-fill, minmax(min(100%, 22rem), 1fr));

/* Tipografía fluida */
font-size: clamp(min, preferred, max);
```

Breakpoint explícito principal: `1024px` para mostrar/ocultar nav desktop vs hamburger.

---

## Cómo cambiar el tema visual

Para una renovación visual completa, los únicos archivos a modificar son:

1. **`src/styles/global.css`** — tokens de color, tipografía, espaciado
2. **Google Fonts URL en `src/layouts/BaseLayout.astro`** — cambiar fuentes
3. Los componentes individuales (`.astro`) usan solo los tokens, no valores hardcoded

Este diseño permite intercambiar el look completo en menos de 30 minutos.
