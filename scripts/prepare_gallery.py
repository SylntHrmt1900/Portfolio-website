#!/usr/bin/env python3
"""Build uncropped gallery previews without modifying supplied source media.

Run from any directory with Python 3, Pillow, PyMuPDF, ffmpeg and ffprobe.
The checked-in manifest and media make this optional for normal site use.
Re-running replaces only this script's generated outputs. Original SHA-256
checksums, dimensions, PDF pages, codecs and byte totals are saved in docs/.
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile

import fitz
from PIL import Image, ImageCms, ImageOps, __version__ as PIL_VERSION


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "WebsiteAssets"
MEDIA = SITE / "gallery/media"
THUMBNAIL_BOUNDS = (1000, 6000)
FULL_BOUNDS = (2400, 12000)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


# Array order is the gallery order. The original seven AI items stay first.
# Descriptions are accessibility text, never visible tile titles/captions.
SOURCES = {
    "ai": ("AI", [
        ("042026 - Social - Agentic AI for Enterprise Operations.jpg", "agentic-enterprise-landscape", "Concentrix Agentic AI campaign with a wanted poster and a message about finding AI impact in a pilot program."),
        ("042026 - Social - Agentic AI for Enterprise Operations2.jpg", "agentic-enterprise-portrait", "Portrait Agentic AI campaign with a wanted poster on a Western street."),
        ("082026 - Graphic Assets - HRiX Evergreen Content 1920x1080.jpg", "hrix-one-window", "HRiX campaign contrasting seventeen open browser tabs with a single HRiX window."),
        ("082026 - Graphic Assets - HRiX Evergreen Content 1920x1080.png", "hrix-search", "HRiX campaign showing a person searching through notes for an answer."),
        ("082026 - Graphic Assets - HRiX Evergreen Content 1920x1080_2.jpg", "hrix-one-place", "HRiX campaign showing workplace questions and the message Different questions. One place to start."),
        ("1-32.png", "nextwave-brief-update", "Nextwave campaign with a towering paper stack and a message about AI turning a brief update into a three-thousand-word novel."),
        ("1.png", "hypercare-halloween", "Hypercare Halloween artwork with a turquoise moon, haunted house, bats and pumpkins."),
        ("1 3.png", "license-puppy", "Concentrix learning-license campaign showing a puppy waiting by a door with an Activate Me tag."),
        ("1 4.png", "ix-hero-roleplay", "Portrait iX Hero roleplay campaign with an advisor seated inside a futuristic training pod."),
        ("1-35.png", "nextwave-shakespeare-desk", "Nextwave campaign showing a man at a desk holding an elaborate scroll after asking AI for a simple email."),
        ("1-36.png", "nextwave-shakespeare-office", "Nextwave campaign showing a Shakespearean character unrolling a long scroll in an office."),
        ("1-39.png", "nextwave-make-it-shorter", "Nextwave campaign with a man working among scattered papers and a message about AI shortening away the important information."),
        ("17.png", "hypercare-forest", "Hypercare Halloween artwork with a skeleton in a dark forest and a glowing tree-hollow sign."),
        ("2 2.png", "hypercare-frankenstein", "Hypercare Halloween illustration of Frankenstein's monster, a small skeleton and jack-o'-lanterns in a forest."),
        ("2.png", "linkedin-learning-waiting", "LinkedIn Learning activation campaign showing two colleagues at a laptop and a reminder to use a saved learning license."),
        ("Game-Changer Day_Teaser_1080x1920.png", "game-changer-legend", "Portrait Game-Changer Day poster featuring a smiling woman and the words You're a Legend."),
    ]),
    "branding": ("Brand Systems", [
        ("012025_Logo_WiseOwls_GRG_LightBG-V2.png", "wiseowls-logo", "WiseOwls wordmark with an owl emblem between the words.", "light"),
        ("032724_BuzzHub_Logo_NewCo-(1).png", "buzzhub-logo", "BuzzHub wordmark with a speech bubble on a dark teal rounded badge.", "dark"),
        ("33 2.png", "legends-talent-contest", "Round Game-Changer Day Legends talent-contest badge with a spotlight."),
        ("4.png", "hrix-manager-evaluation", "HRiX manager-evaluation campaign featuring a man using a laptop and a three-step process graphic."),
        ("5Tips_Banner_Revised2.png", "patient-member-experiences", "Healthcare campaign banner promoting five tips for effortless patient and member experiences, beside a masked clinician and patient."),
        ("7.png", "saved-courses", "Learning-license campaign showing a person surrounded by saved course windows."),
        ("Artboard 4 copy 16.png", "ixhero-social-post", "iX Hero social-media post featuring an advisor holding a tablet and a forty-percent faster-response message."),
        ("Culture-Roadshow-Graphic.png", "culture-roadshow", "Concentrix Culture Roadshow 2024 badge with colorful heart-shaped figures.", "dark"),
        ("DBR Blue.png", "design-build-run", "Circular white Design Build Run badge with navy lettering and orange, yellow and turquoise dots."),
        ("GTALogoFinal_320x104px.png", "gatehouse-associates", "GateHouse Associates logo with a red arched symbol and dark lettering.", "light"),
        ("IX-Hero_Prelaunch_Carousel_1.png", "cognitive-overload-audit", "Portrait campaign graphic titled How to Conduct a Cognitive Overload Audit, featuring a woman with a tablet."),
        ("NewCo_PC-Logo_Badge_FullColor.png", "presidents-club", "Concentrix President's Club Awards circular badge with a turquoise star.", "light"),
        ("ReimaginePatientCX_Li_Opt2.png", "reimagine-patient-cx", "Healthcare banner about reimagining the patient experience with AI, featuring a clinician speaking with a patient."),
        ("badge_LCNCNew.png", "lcnc-citizen-developer", "LCNC Citizen Developer badge with a computer illustration on a teal background.", "dark"),
        ("iX-Hero-Samples_2-1.png", "meet-our-heroes", "Concentrix social-media post introducing a technical-support advisor beside an iX Hero campaign graphic."),
    ]),
    "executive": ("Executive Presentation", [
        ("082026 - Your Week in 5 - Email newsletter refresh.png", "your-week-in-five-refresh", "Complete Your Week in 5 email newsletter with a header collage, teal feature panels, news cards and footer."),
        ("1 3.png", "linkedin-learning-email-one", "LinkedIn Learning email design with two colleagues in the header, learning categories and a sign-up button."),
        ("2 3.png", "linkedin-learning-email-two", "LinkedIn Learning email variation with a man in the header, learning categories and a sign-up button."),
        ("2.png", "your-week-in-five-dark", "Complete Your Week in 5 newsletter with a dark teal header and stacked articles, image cards and resource links."),
        ("3.png", "your-week-in-five-light", "Complete Your Week in 5 newsletter variation with a light header and stacked articles, image cards and resource links."),
        ("BuzzHub - Newsletters 2.png", "buzzhub-newsletter", "BuzzHub newsletter introducing Concentrix, with a glowing planet, performance features and employee story cards."),
        ("Email_LeadershipAcademy_Director.png", "leadership-academy-director", "Director's Academy email announcement with a man beside a turquoise smiley and future-leader program details."),
        ("Email_LeadershipAcademy_SrManager.png", "leadership-academy-manager", "Senior Manager's Academy email announcement with a woman beside a turquoise smiley and leadership-program details."),
        ("Final Newsletter Layout.png", "buzzhub-newsletter-layout", "BuzzHub email layout with a We're Concentrix header, enterprise-performance features and employee story cards."),
        ("iX Hello Newsletter .png", "ix-hello-newsletter", "iX Hello Momentum newsletter with product updates, a featured speaker, customer stories and a community section."),
    ]),
    "uiux": ("UI-UX", [
        ("012026 - Adobe AI Ecommerce Virtual Partner Event.pdf", "adobe-ai-ecommerce-event", "Full Adobe AI ecommerce event landing-page design with a turquoise AI illustration, event details and registration form."),
        ("082026 - NR Phase 2 Campaign Landing Page - V1.pdf", "nr-campaign-landing-page", "Complete Concentrix campaign landing-page design with teal hero, service sections, photography and registration form."),
        ("122025 - iX Hello - Chat Bot Hero - Option 2.png", "ix-hello-chatbot", "iX Hello chatbot website design with a waveform hero, product panel, capability sections and a contact form."),
        ("Enterprise Performance Landing Page.pdf", "enterprise-performance", "Enterprise-performance landing-page design with a dark teal hero, customer-service photography, solution cards and contact form."),
        ("Frame 13.png", "value-creation-products", "Supercharging Value Creation webpage featuring a glowing turquoise capsule and iX product cards."),
        ("Hero - Engineering.png", "hero-engineering", "Concentrix engineering webpage hero with abstract teal and gold lighting and the words Engineer systems that make transformation executable."),
        ("Hero - Intelligence.png", "hero-intelligence", "Concentrix intelligence webpage hero with abstract teal lighting and a message about activating intelligence for enterprise performance."),
        ("Hero - Strategy - Option 2.png", "hero-strategy", "Concentrix strategy webpage hero with teal and gold lighting and a Human plus AI transformation message."),
        ("Home Page 4.17.2026 v1.pdf", "homepage-design", "Complete Concentrix homepage design with a glowing turquoise hero, service panels, photography, industry cards and footer."),
        ("Industries.png", "industries-grid", "Concentrix industries webpage section with a grid of industry icons and descriptions on a teal background."),
        ("iX Website - Product Page 2 - Advisor Assist V2.png", "advisor-assist-product", "Advisor Assist product-page hero showing an advisor at a monitor with floating assistance messages."),
    ]),
    "motion": ("Videos", [
        ("AgenticValueMap_Retail_FINAL 2.mp4", "agentic-value-map-retail", "Agentic Value Maps motion graphic with colored transit-style lines illustrating Human plus AI collaboration."),
        ("CNXU_Video_RevisedFeb14 2.mp4", "concentrix-university", "Concentrix University promotional animation with turquoise graphics, course information and learning messages."),
        ("Coachcentrix Program Promotional Video_Revised_Feb11 2.mp4", "coachcentrix-program", "Coachcentrix training-program promotional video with animated typography on a teal background."),
        ("Gen-4 Create a short animated video of a few dark blue shopping bags falling down from the top using parachutes The parachutes gently guide the bags down, creating a whimsical and elegant delivery ef (1).mp4", "parachute-shopping-bags", "Portrait animation of branded shopping bags descending on parachutes inside a multistory shopping mall."),
        ("KOM23 Intro - Outro.mp4", "kom23-intro-outro", "Concentrix event intro and outro animation with brand graphics and people against colorful backgrounds."),
        ("WisdomAnim3.mp4", "wisdom-brand-animation", "Concentrix brand animation transitioning between the wordmark and the iX symbol."),
    ]),
}


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def site_path(path: Path) -> str:
    if path.is_relative_to(SITE):
        return path.relative_to(SITE).as_posix()
    return "../" + path.relative_to(ROOT).as_posix()


def file_record(path: Path, **metadata) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": sha256(path), **metadata}


def save_webp(image: Image.Image, path: Path, bounds: tuple[int, int], quality: int) -> tuple[int, int]:
    result = image.copy()
    profile = result.info.get("icc_profile")
    if profile:
        # Several supplied JPEGs use Adobe RGB. Convert pixels before dropping
        # the profile so untagged browser output retains the intended colors.
        alpha = result.getchannel("A") if "A" in result.getbands() else None
        result = ImageCms.profileToProfile(
            result.convert("RGB"), ImageCms.ImageCmsProfile(io.BytesIO(profile)),
            ImageCms.createProfile("sRGB"), outputMode="RGB",
        )
        if alpha is not None:
            result.putalpha(alpha)
    result.thumbnail(bounds, Image.Resampling.LANCZOS)
    if result.mode not in ("RGB", "RGBA"):
        result = result.convert("RGBA" if "transparency" in result.info else "RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exact alpha retention prevents dark/light logo edges being composited.
    result.save(path, "WEBP", quality=quality, method=6, exact=True)
    return result.size


def probe(path: Path) -> dict:
    return json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)))


def stream_metadata(info: dict) -> list[dict]:
    fields = ("codec_type", "codec_name", "width", "height", "pix_fmt", "avg_frame_rate", "sample_rate", "channels", "duration")
    return [{key: stream[key] for key in fields if key in stream} for stream in info["streams"]]


def image_items(source: Path, category: str, item_id: str, alt: str, surface: str | None) -> tuple[list[dict], list[dict], dict]:
    is_pdf = source.suffix.lower() == ".pdf"
    document = fitz.open(source) if is_pdf else None
    if document is not None and document.is_encrypted:
        raise RuntimeError(f"Cannot render encrypted PDF: {source}")
    page_count = len(document) if document is not None else 1
    if not page_count:
        raise RuntimeError(f"No pages in PDF: {source}")
    items, outputs, page_metadata = [], [], []
    try:
        for page_index in range(page_count):
            if document is not None:
                page = document[page_index]
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
                image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
                page_metadata.append({"page": page_index + 1, "points": [page.rect.width, page.rect.height], "rendered_pixels": list(image.size)})
            else:
                with Image.open(source) as original:
                    image = ImageOps.exif_transpose(original).copy()
            entry_id = f"{item_id}-page-{page_index + 1}" if document is not None else item_id
            full = MEDIA / category / f"{entry_id}.webp"
            thumbnail = MEDIA / category / f"{entry_id}-thumb.webp"
            full_size = save_webp(image, full, FULL_BOUNDS, 88)
            thumbnail_size = save_webp(image, thumbnail, THUMBNAIL_BOUNDS, 82)
            item = {"id": entry_id, "type": "image", "src": site_path(full),
                    "thumbnail": site_path(thumbnail), "width": full_size[0], "height": full_size[1],
                    "alt": alt, "original": site_path(source)}
            if surface:
                item["surface"] = surface
            if document is not None:
                item.update({"page": page_index + 1, "pageCount": page_count})
                if page_count > 1:
                    item["alt"] += f" Page {page_index + 1} of {page_count}."
            items.append(item)
            outputs.extend([file_record(full, role="full", width=full_size[0], height=full_size[1]),
                            file_record(thumbnail, role="thumbnail", width=thumbnail_size[0], height=thumbnail_size[1])])
            image.close()
        metadata = {"kind": "pdf" if document is not None else "image"}
        if document is not None:
            metadata.update({"page_count": page_count, "pages": page_metadata})
        else:
            with Image.open(source) as original:
                metadata.update({"width": original.width, "height": original.height, "mode": original.mode})
        return items, outputs, metadata
    finally:
        if document is not None:
            document.close()


def video_item(source: Path, category: str, item_id: str, alt: str) -> tuple[list[dict], list[dict], dict]:
    info = probe(source)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next((stream for stream in info["streams"] if stream["codec_type"] == "audio"), None)
    duration = float(info["format"]["duration"])
    width, height = video["width"], video["height"]
    output_dir = MEDIA / category
    output_dir.mkdir(parents=True, exist_ok=True)
    thumbnail = output_dir / f"{item_id}-poster.webp"
    # Use a representative interior frame instead of an opening fade/logo.
    poster_time = round(duration * 0.35, 3)
    poster_data = subprocess.check_output([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(poster_time), "-i", str(source),
        "-frames:v", "1", "-threads", "2", "-f", "image2pipe", "-vcodec", "png", "pipe:1",
    ])
    with Image.open(io.BytesIO(poster_data)) as poster:
        poster_size = save_webp(poster, thumbnail, (1000, 1000), 84)
    outputs = [file_record(thumbnail, role="poster", width=poster_size[0], height=poster_size[1])]
    optimized = output_dir / f"{item_id}.mp4"
    maximum_scale = min(1, 1920 / width, 1920 / height)
    target_width = max(2, int(width * maximum_scale) // 2 * 2)
    target_height = max(2, int(height * maximum_scale) // 2 * 2)
    with tempfile.TemporaryDirectory(prefix="portfolio-video-") as temporary:
        candidate = Path(temporary) / "optimized.mp4"
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(source),
                   "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "libx264", "-preset", "medium",
                   "-crf", "24", "-pix_fmt", "yuv420p", "-threads", "2"]
        if (target_width, target_height) != (width, height):
            command.extend(["-vf", f"scale={target_width}:{target_height}"])
        if audio is not None:
            command.extend(["-c:a", "copy"] if audio["codec_name"] == "aac" else ["-c:a", "aac", "-b:a", "160k"])
        command.extend(["-movflags", "+faststart", "-y", str(candidate)])
        subprocess.run(command, check=True)
        candidate_info = probe(candidate)
        candidate_video = next(stream for stream in candidate_info["streams"] if stream["codec_type"] == "video")
        candidate_audio = next((stream for stream in candidate_info["streams"] if stream["codec_type"] == "audio"), None)
        if candidate_video["codec_name"] != "h264" or candidate_video["pix_fmt"] != "yuv420p":
            raise RuntimeError(f"Unexpected video codec for {source}")
        if bool(audio) != bool(candidate_audio) or abs(float(candidate_info["format"]["duration"]) - duration) > 0.15:
            raise RuntimeError(f"Audio or duration changed for {source}")
        if (candidate_video["width"], candidate_video["height"]) != (target_width, target_height):
            raise RuntimeError(f"Unexpected video dimensions for {source}")
        # Decode every frame to catch unusable outputs before selecting them.
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(candidate),
                        "-threads", "2", "-f", "null", "-"], check=True)
        if candidate.stat().st_size < source.stat().st_size:
            optimized.write_bytes(candidate.read_bytes())
            selected = optimized
            width, height = target_width, target_height
            outputs.append(file_record(optimized, role="video", width=width, height=height,
                                       duration_seconds=float(candidate_info["format"]["duration"]),
                                       streams=stream_metadata(candidate_info)))
        else:
            selected = source
            if optimized.exists():
                optimized.unlink()
    item = {"id": item_id, "type": "video", "src": site_path(selected),
            "thumbnail": site_path(thumbnail), "width": width, "height": height,
            "alt": alt, "original": site_path(source)}
    metadata = {"kind": "video", "width": video["width"], "height": video["height"],
                "duration_seconds": duration, "streams": stream_metadata(info),
                "poster_time_seconds": poster_time, "optimized_selected": selected == optimized}
    return [item], outputs, metadata


def main() -> None:
    manifest = {key: [] for key in ("uiux", "motion", "branding", "elearning", "ai", "executive")}
    inventory_sources = []
    all_outputs = []
    for category, (folder, records) in SOURCES.items():
        directory = ROOT / folder
        actual = {path.name for path in directory.iterdir() if not path.name.startswith(".") and path.is_file()}
        declared = {record[0] for record in records}
        if actual != declared or len(declared) != len(records):
            raise RuntimeError(f"Media inventory mismatch in {folder}: unlisted={actual - declared}; missing={declared - actual}")
        for record in records:
            filename, item_id, alt, *surface = record
            source = directory / filename
            checksum_before = sha256(source)
            print(f"Preparing {category}/{item_id}", flush=True)
            if source.suffix.lower() == ".mp4":
                items, outputs, metadata = video_item(source, category, item_id, alt)
            elif source.suffix.lower() in IMAGE_EXTENSIONS | {".pdf"}:
                items, outputs, metadata = image_items(source, category, item_id, alt, surface[0] if surface else None)
            else:
                raise RuntimeError(f"Unsupported source: {source}")
            if sha256(source) != checksum_before:
                raise RuntimeError(f"Original media changed during preparation: {source}")
            manifest[category].extend(items)
            inventory_sources.append(file_record(source, category=category, gallery_ids=[item["id"] for item in items],
                                                 **metadata, outputs=outputs))
            all_outputs.extend(outputs)
    MEDIA.mkdir(parents=True, exist_ok=True)
    manifest_file = SITE / "gallery/works.js"
    manifest_file.write_text(
        "// Generated by scripts/prepare_gallery.py. Paths are relative to WebsiteAssets/index.html.\n"
        "// Accessibility descriptions are never displayed as tile titles or captions.\n"
        "window.PORTFOLIO_WORKS = " + json.dumps(manifest, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    totals = {
        "original_files": len(inventory_sources),
        "original_images": sum(source["kind"] == "image" for source in inventory_sources),
        "original_pdfs": sum(source["kind"] == "pdf" for source in inventory_sources),
        "pdf_pages": sum(source.get("page_count", 0) for source in inventory_sources),
        "original_videos": sum(source["kind"] == "video" for source in inventory_sources),
        "gallery_items": sum(len(items) for items in manifest.values()),
        "items_per_category": {key: len(items) for key, items in manifest.items()},
        "original_bytes": sum(source["bytes"] for source in inventory_sources),
        "generated_files": len(all_outputs),
        "generated_bytes": sum(output["bytes"] for output in all_outputs),
        "thumbnail_bytes": sum(output["bytes"] for output in all_outputs if output["role"] in ("thumbnail", "poster")),
        "full_image_bytes": sum(output["bytes"] for output in all_outputs if output["role"] == "full"),
        "optimized_video_bytes": sum(output["bytes"] for output in all_outputs if output["role"] == "video"),
    }
    inventory = {
        "generator": "scripts/prepare_gallery.py", "schema_version": 1,
        "tools": {"pillow": PIL_VERSION, "pymupdf": fitz.VersionBind,
                  "ffmpeg": run("ffmpeg", "-version").splitlines()[0]},
        "settings": {"thumbnail_bounds": list(THUMBNAIL_BOUNDS), "thumbnail_webp_quality": 82,
                     "full_image_bounds": list(FULL_BOUNDS), "full_webp_quality": 88,
                     "color_profile": "Convert embedded ICC profiles to sRGB before WebP export",
                     "pdf_pixels_per_point": 1, "video_crf": 24, "video_threads": 2,
                     "video_maximum_dimension": 1920, "crop": False, "upscale": False,
                     "video_audio": "copy AAC; otherwise AAC 160k", "video_faststart": True},
        "totals": totals, "sources": inventory_sources,
    }
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/media-inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2), flush=True)


if __name__ == "__main__":
    main()
