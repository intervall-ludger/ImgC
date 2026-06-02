[![CI](https://github.com/intervall-ludger/ImgC/actions/workflows/ci.yml/badge.svg)](https://github.com/intervall-ludger/ImgC/actions/workflows/ci.yml)

# ImgC — Image Optimizer

ImgC converts an image (or a whole folder) between formats and, on request,
**squeezes it to a target file size** — it steps down the JPEG quality and
downscales until the result fits your `--max` (or upscales to reach a `--min`).

One Rust core, two front-ends:

- **Web app** — Rust compiled to WebAssembly, runs entirely in your browser.
  Images are never uploaded; nothing leaves your device.
- **CLI** — a native `imgc` binary for scripting and batch jobs.

**▶ Live app: https://intervall-ludger.github.io/ImgC/**

## Why

ImgC grew out of academic writing. Two problems kept coming up:

1. **Journals demand a specific format** — TIFF, a PDF figure, a fixed
   resolution — so you have to convert your figures anyway.
2. **Word ruins high-resolution images.** Drop a large PNG into a document and
   Word silently re-compresses it on its own terms, often turning a crisp
   figure into a blurry one for your co-authors and reviewers.

The cure is to **compress deliberately before embedding**: shrink the figure to
a sensible size yourself, then place the already-optimized file. Word is left
with nothing to mangle, the document stays small, and everyone sees the figure
the way you intended.

```bash
# Typical figure prep: a 300-dpi PNG export, capped at 800 KB, ready for Word
imgc -f figure_1.png -s jpg --max 0.8
```

## Supported formats

| Direction | Formats |
| --- | --- |
| **Read** | PNG, JPG, TIFF, GIF, ICO, WebP, BMP, **DICOM** (`.dcm`, uncompressed), **HEIC/HEIF** (CLI only — see [HEIC input](#heicheif-input-optional)) |
| **Write** | PNG, JPG, TIFF, GIF (animated), ICO, WebP (lossless), PDF |

Size targeting (`--max`/`--min`) applies to the raster and PDF outputs.

## Web app

Open the [live app](https://intervall-ludger.github.io/ImgC/) (or run it locally —
see [below](#building--running-locally)), drop in one or more images, choose the
output format and options, and download the result. Everything happens locally
via WebAssembly; there is no backend. Choosing **GIF** with several images
combines them into one animated GIF.

## CLI

Run straight from the workspace:

```bash
cargo run -p imgc-cli -- -f /path/to/image -s png [options]
```

…or install the `imgc` binary:

```bash
cargo install --path crates/imgc-cli
```

### Options

| Flag | Description |
| --- | --- |
| `-f, --filename` | Image file or folder of images to convert |
| `-s, --suffix` | Output format: `png`, `jpg`, `tif`, `gif`, `ico`, `webp`, `pdf` |
| `--filter_suffix` | In folder mode, only process inputs with this extension |
| `--max` | Maximum output size in MB |
| `--min` | Minimum output size in MB |
| `--fps` | Frames per second for animated GIF output (default 30) |
| `--size` | Pixel size for ICO output (default 64) |

Pointing `-f` at a folder converts every matching file in place (next to the
original). With `-s gif`, a folder of stills is combined into one animated GIF
named after the folder.

### Examples

```bash
# Convert to PNG, capped at 2 MB and at least 1 MB
imgc -f photo.jpg -s png --max 2 --min 1

# Convert every JPG in a folder to TIFF
imgc -f ./shots -s tif --filter_suffix jpg

# A 16-bit CT scan to a viewable PNG
imgc -f scan.dcm -s png

# A 24 fps animated GIF from a folder of frames
imgc -f ./frames -s gif --fps 24
```

### HEIC/HEIF input (optional)

HEIC has no usable pure-Rust decoder, so it lives behind the `heic` Cargo
feature and relies on the system
[`libheif`](https://github.com/strukturag/libheif) library. It is therefore
**CLI-only** — the web build stays pure Rust with no native dependency.

```bash
# macOS:  brew install libheif
# Debian: sudo apt-get install libheif-dev
cargo install --path crates/imgc-cli --features heic
imgc -f photo.heic -s jpg --max 0.5
```

## How it works

```
crates/
  imgc-core/   platform-agnostic conversion library (bytes in -> bytes out)
  imgc-cli/    native command-line interface
  imgc-wasm/   wasm-bindgen bindings for the web app
web/           static front-end (HTML/CSS/JS), loads the generated pkg/
```

All decoding, resizing, size-fitting and encoding lives in `imgc-core` and never
touches the filesystem — bytes in, bytes out. The CLI handles file I/O, the web
app handles browser I/O, and both call the exact same core, so they behave
identically.

## Building & running locally

The CLI needs only a Rust toolchain. The web app additionally needs
[`wasm-pack`](https://rustwasm.github.io/wasm-pack/):

```bash
# Build the WebAssembly bundle into web/pkg
wasm-pack build crates/imgc-wasm --target web --out-dir ../../web/pkg --out-name imgc

# Serve the static front-end (ES modules need HTTP, not file://)
cd web && python3 -m http.server 8080
# then open http://localhost:8080
```

## Development

```bash
cargo test --workspace      # unit + CLI integration tests (incl. a real DICOM)
cargo fmt --all             # format
cargo clippy --all-targets  # lint
```

CI runs format, clippy, the full test suite and a wasm build on every push; a
separate job installs `libheif` and exercises the `heic` feature. Pushing to
`main` rebuilds the WebAssembly bundle and deploys `web/` to GitHub Pages.

> **One-time setup for deployment:** in the repository settings, set
> *Pages → Build and deployment → Source* to **GitHub Actions**.

## Notes & limitations

- **WebP** output is lossless only — the pure-Rust encoder has no lossy mode yet.
- **DICOM** input is read for uncompressed pixel data.
- **HEIC/HEIF** input is CLI-only and needs `libheif`; HEIC output is not supported.
- **MP4** is not supported; combine multiple images into an animated GIF instead.

## License

ImgC is licensed under the GNU General Public License v3. See [LICENSE](./LICENSE).
