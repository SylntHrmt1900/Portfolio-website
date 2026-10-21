# RESTORED ORIGINAL DESIGN — PRESERVE THE COMPOSITION

The live source is `WebsiteAssets/index.html`. Keep the dark cinematic editorial
direction: background #0E1116, glass surface #161B22, amber #F5B921, cobalt
#3B82F6, light text #F5F7FA. Fonts are Plus Jakarta Sans and Playfair Display.
Preserve the rounded photographic portrait and the existing authored career content.

## Two-view architecture

- `#homeView` holds the homepage, six folder cards, and filters.
- `#categoryView` is the separate category page shown after selecting a folder.
- Preserve its header, breadcrumb, quick-switcher, and Back to Homepage control.
- `openCategory()`, `navigateToHome()` and hash routing retain browser history.
- Never move `#categoryFilterContainer` or `#portfolioFolderGrid` outside `#work`.
- Keep category IDs `uiux`, `motion`, `branding`, `elearning`, `ai`, `executive`.
- Root `index.html` is a Pages entry redirect; asset paths remain relative to the app.

## Actual media galleries

`gallery/works.js` supplies every uploaded work. The shared renderer and styles
are `portfolio-gallery.js` and `portfolio-gallery.css`.

- Show image/media tiles only: no titles, descriptions, client badges, dates,
  artificial project counts, or hover captions.
- Always contain the full artwork; never crop or stretch it. Long documents
  fit in a bounded preview and support zoom/scroll in the dialog.
- Neutral light plates make transparent dark logos visible without modifying them.
- Video tiles use actual posters with a play icon, native controls and no autoplay.
- Keep original artwork and PDF/video files; optimize separate generated copies.
- eLearning is pending. Keep a navigable, honest empty state until its media arrives.
- Use soft 1.3-second reveals, brief capped staggers, and the AI pilot's
  600ms preview opening / 320ms closing. Respect reduced motion.
- Retain Escape, previous/next, focus trapping/restoration and gallery scroll position.

Do not add new promotional sections, fictional projects, synthetic SVG work,
metrics or career claims. Keep the contact form truthful about email-client
submission and the CV action truthful about requesting a file by email.
