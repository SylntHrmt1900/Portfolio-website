# Rajakumar M — Creative Portfolio

[Open the portfolio](https://sylnthrmt1900.github.io/Portfolio-website/)

The root `index.html` opens `WebsiteAssets/index.html`, preserving category
links and query strings. `.nojekyll` makes GitHub Pages serve the static site;
the project root now opens the portfolio instead of rendering this README.
The existing Pages deployment uses `main` and the repository root.

## Selected Work

| Category | Uploaded works | Contents |
| --- | ---: | --- |
| UI/UX & Web | 11 | Seven images and four complete PDF page previews |
| Motion & Video | 6 | Video posters and on-demand HTML5 playback |
| Brand & Campaigns | 15 | Campaign artwork, logos, and identity assets |
| AI Creative Pipelines | 16 | Original seven pieces plus nine newly uploaded works |
| Executive Presentation & Comms | 10 | Newsletters and communication designs |
| eLearning & Interactive | Pending | Category and navigation retained; no fabricated projects |

All 58 supplied works are connected through `WebsiteAssets/gallery/works.js`.
Tiles show complete, proportionally scaled artwork without titles or captions.
Long pages fit inside the tile; the preview's zoom control lets visitors read
and scroll the detail. The original-file control opens the untouched image,
PDF, or video in a new tab. Video tiles show a play control; playback starts
only when requested and stops when changing items or closing the preview.

The homepage composition, portrait, category headers, career history, Infosys
feature, and navigation remain in place. Every work folder and gallery uses
the AI pilot's soft fade/movement and viewport stagger. Preview opening and
closing respect reduced-motion preferences, preserve focus and scroll, and
support keyboard controls.

## Image and video optimization

The supplied originals remain untouched in `AI/`, `Brand Systems/`,
`Executive Presentation/`, `UI-UX/`, and `Videos/`. The manifest points to
optimized copies under `WebsiteAssets/gallery/media/`:

- About **39.7 MB of generated media versus 160.1 MB of originals**, including
  both thumbnails and full previews (about 75% smaller).
- WebP previews preserve aspect ratio and transparency; no cropping/upscaling.
  Embedded Adobe RGB artwork is converted to sRGB for consistent browser color.
- Full PDF pages are rendered as image previews; original PDFs remain linked.
- Six H.264 videos use faststart, retain their proportions/audio, and load on demand.
- Gallery images are lazy-loaded; full image previews decode before replacing
  their lightweight thumbnail.

`docs/media-inventory.json` records every source, output, checksum, dimension,
PDF page count, codec, and byte total. `docs/website-update.md` records this pass.

## Preview and update

Serve the repository root with any static web server, for example:

```sh
python3 -m http.server 8000
```

Open the server's root in a browser. Keep the folder structure intact. The
existing fonts, Tailwind styling, and Lenis load from external CDNs, requiring
an Internet connection. No app build or backend service is needed.

`WebsiteAssets/index.html` is the live app source; `WebsiteAssets/code.html`
is the original reference export. Shared rendering and styles live in
`WebsiteAssets/portfolio-gallery.js` and `WebsiteAssets/portfolio-gallery.css`.
The old AI-only files remain for compatibility with earlier cached previews.

For future uploads, add the original files, then update `SOURCES` in
`scripts/prepare_gallery.py` with their category, ordering and accessibility
text. Install Pillow and PyMuPDF and have `ffmpeg`/`ffprobe` available, then run:

```sh
python3 scripts/prepare_gallery.py
```

The script refuses to silently omit unlisted files and regenerates only its
optimized outputs, manifest, and inventory. For eLearning, add its folder and
records to `SOURCES`; keep the existing `elearning` category ID. Normal site
viewing uses the checked-in generated files and needs no Python packages.

Push completed changes to `main`; the existing GitHub Pages job republishes
the website. After its successful run, refresh the site to pick up the update.

## Contact and CV

The contact form validates input, preserves it, and opens an encoded email
draft. Visitors must send that draft in their email application; the site
never claims delivery. No email backend or frontend API key is invented.
The CV action is accurately labeled **Request CV by Email** because no resume
PDF has been supplied. The UI/UX PDFs are portfolio work, not resume files.
