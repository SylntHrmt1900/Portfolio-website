# Portfolio-website

Rajakumar M's portfolio. The live entry point is **WebsiteAssets/index.html**;
`WebsiteAssets/code.html` is the original reference export.

## Preview the AI gallery

Open `WebsiteAssets/index.html` in a browser, then select the **AI Creative
Pipelines** folder under Selected Work. You can also serve the whole repository:

```sh
python3 -m http.server 8000
```

Open `WebsiteAssets/index.html` through that local server. Keep `AI/` and
`WebsiteAssets/` together; original images use relative paths between them.
The existing site loads Tailwind, Lenis, and fonts from external CDNs, so an
Internet connection is required for its original styling and scrolling.

## This pilot

- Only AI now displays the seven uploaded artworks as image-only tiles.
- Every tile shows the complete image at its natural proportions.
- Click a tile for the full-resolution original in a dialog. Use the close
  button, Escape, or the backdrop to return to the same gallery position.
- Previous/next buttons and Left/Right keys move between artworks.
- The original homepage, category headers, quick-switch tabs, and return
  navigation are retained. The other five categories still contain the
  original demonstration projects and are awaiting their own artwork pass.

## Artwork files

`AI/` contains the untouched originals. `WebsiteAssets/gallery/ai/` contains
1200px-wide WebP previews, resized proportionally without cropping. Together
these previews are about 0.8 MB; full-size originals load when opened.

`WebsiteAssets/gallery/ai-artworks.js` controls artwork order, original paths,
preview paths, dimensions, and screen-reader descriptions. To add an image,
keep its original in `AI/`, create an uncropped proportional WebP preview, and
add an entry to that manifest. Paths are relative to `WebsiteAssets/index.html`.
Descriptions are accessibility labels and are never shown as tile captions.

The renderer and dialog are in `WebsiteAssets/ai-gallery.js`; their styles are
scoped in `WebsiteAssets/ai-gallery.css`. No build tool is required to run them.

Publication, the remaining category galleries, and the existing contact/CV
behavior are outside this AI-only pass.
