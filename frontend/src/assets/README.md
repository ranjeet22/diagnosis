# Diagnōsis Visual Assets Guide & Specifications

This directory houses the design system's visual assets. All assets must conform to the consistent **Modern medical SaaS** style language defined below.

---

## 🎨 Consistent Design Language

* **Style**: Soft Clay 3D + Matte Glass overlays.
* **Colors**: Medical Blue (`#2563EB`), Sky Blue, White, soft clay pastel accents.
* **Geometry**: Rounded vertices, smooth contours, minimal details.
* **Perspective**: 45-degree angle projections, soft shadows, floating states.

---

## 📦 Required 3D Assets (Clay style / `.webp` or `.png`)

Place these in `src/assets/3d/`:

| Asset Name | Purpose | Dimensions | Transparent? | Priority |
| :--- | :--- | :--- | :--- | :--- |
| `medical-ai-brain.webp` | Hero Section illustration | 800x800 | Yes | CRITICAL |
| `floating-dashboard.webp` | Product capabilities teaser | 1200x800 | Yes | HIGH |
| `analytics-cube.webp` | Data computation visual | 500x500 | Yes | MEDIUM |
| `data-cloud.webp` | File ingestion pipeline | 600x600 | Yes | HIGH |
| `semantic-network.webp` | Healthcare ontology mapping | 700x700 | Yes | HIGH |
| `ai-chip.webp` | Computation engine performance | 500x500 | Yes | MEDIUM |
| `medical-records.webp` | HIPAA compliance and records | 600x600 | Yes | HIGH |
| `shield-security.webp` | Security and audit validation | 550x550 | Yes | HIGH |
| `chat-assistant.webp` | Conversational analytics interface | 600x600 | Yes | HIGH |
| `floating-chart.webp` | Layout recommendation engine teaser | 800x600 | Yes | MEDIUM |

---

## 🖌️ Illustrations Guide

Place these in `src/assets/illustrations/`:

1. **Hero Illustration** (`hero-teaser.svg`):
   * *Style*: Clean, modern outline vectors showing database nodes connecting to a central diagnostic node.
2. **Deterministic Flow** (`deterministic-architecture.svg`):
   * *Style*: Horizontal chart showing raw CSV data executing locally into metric summaries, passing only metadata keys to Gemini.
3. **Security Shield** (`security-shield.svg`):
   * *Style*: Glassmorphic padlock and clinical records envelope, conveying encryption.

---

## 🌌 Background Patterns & Textures

Place these in `src/assets/patterns/` & `src/assets/backgrounds/`:

* **`grid-pattern.svg`**: Light border-grid lines, opacity 0.04.
* **`dots-pattern.svg`**: Radial dots mesh background, opacity 0.05.
* **`noise-texture.png`**: Micro grain overlay to add premium tactile qualities to glass cards.

---

## 🎬 Lottie Animations

Place these in `src/assets/lottie/`:

* **`dataset-uploading.json`**: Pulsing document icon moving into a cloud loop.
* **`analytics-thinking.json`**: Orbiting calculation nodes showing database operations.
* **`gemini-sparkle.json`**: Soft clinical sparkle transitions when insights generation executes.
* **`success-confetti.json`**: Green ring trigger when ingestion auditing validation checks pass.

---

## 🖥️ Screen Mockups (Figma Exports)

Place screenshots in `src/assets/screenshots/`:

* **`dashboard-overview.png`**: Landing page dashboard teaser (1920x1080).
* **`chat-interface.png`**: Conversational intent router panel preview (1000x800).
* **`layout-builder.png`**: Dashboard page coordinates wrapper builder screen.
