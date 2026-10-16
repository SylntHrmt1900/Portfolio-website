# RESTORED ORIGINAL DESIGN — DO NOT REDESIGN

The source of truth for this website is `index.html`. Preserve the premium DARK cinematic editorial design.

Palette: background #0E1116, glass surface #161B22, amber CTA #F5B921, cobalt-blue lighting #3B82F6, text #F5F7FA.
Typography: Plus Jakarta Sans with Playfair Display italic accents.

## CRITICAL: Two-view architecture (keep exactly)
- Homepage `#homeView` contains all original sections, six folder cards and category filters.
- Separate category page view `#categoryView` replaces the homepage visually when any folder is opened. The separate category-view HEADER contains a "Back to Homepage" button.
- `openCategory()` shows `#categoryView` and hides `#homeView`, `navigateToHome()` reverses the change and returns to `#work`.
- Preserve hash routing and browser history.
- Never move `#categoryFilterContainer` or `#portfolioFolderGrid` outside of `#work` or `#homeView`.
- Preserve category header, breadcrumb, quick-switcher and category page layout.

## Future artwork-only requirement (not implemented until user provides files)
Only when actual artwork files are supplied, replace project cards INSIDE `#catViewProjectsGrid` with artwork-only image tiles, preserving existing category view routing and surrounding layout. Opening an artwork should show an enlarged lightbox. Do not clear existing demo content until the real assets are available and verified.

Do not introduce extra galleries, an empty-manifest replacement, filler banners, or new homepage sections.
