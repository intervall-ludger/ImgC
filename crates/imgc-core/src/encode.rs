use crate::{ConvertOptions, ImgcError};
use image::codecs::gif::{GifEncoder, Repeat};
use image::codecs::jpeg::JpegEncoder;
use image::codecs::webp::WebPEncoder;
use image::{Delay, DynamicImage, ExtendedColorType, Frame, ImageFormat};
use std::io::Cursor;

const MAX_PIXEL_SIZE: u32 = 8000;
const MIN_PIXEL_SIZE: u32 = 16;
const MAX_UPSCALE_SIZE: u32 = 20000;
const SIZE_ITER_CAP: u32 = 40;
const START_QUALITY: u8 = 95;
const MIN_QUALITY: u8 = 20;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OutputFormat {
    Png,
    Jpeg,
    Tiff,
    Gif,
    Ico,
    WebP,
    Pdf,
}

impl OutputFormat {
    pub fn from_extension(ext: &str) -> Option<Self> {
        match ext.trim_start_matches('.').to_ascii_lowercase().as_str() {
            "png" => Some(Self::Png),
            "jpg" | "jpeg" => Some(Self::Jpeg),
            "tif" | "tiff" => Some(Self::Tiff),
            "gif" => Some(Self::Gif),
            "ico" => Some(Self::Ico),
            "webp" => Some(Self::WebP),
            "pdf" => Some(Self::Pdf),
            _ => None,
        }
    }

    pub fn extension(self) -> &'static str {
        match self {
            Self::Png => "png",
            Self::Jpeg => "jpg",
            Self::Tiff => "tif",
            Self::Gif => "gif",
            Self::Ico => "ico",
            Self::WebP => "webp",
            Self::Pdf => "pdf",
        }
    }

    fn is_lossy(self) -> bool {
        matches!(self, Self::Jpeg)
    }
}

pub fn encode(
    img: DynamicImage,
    format: OutputFormat,
    opts: &ConvertOptions,
) -> Result<Vec<u8>, ImgcError> {
    match format {
        OutputFormat::Ico => encode_ico(&img, opts.icon_size),
        OutputFormat::Gif => encode_animated_gif(std::slice::from_ref(&img), opts),
        _ => encode_with_size(img, format, opts),
    }
}

fn encode_once(
    img: &DynamicImage,
    format: OutputFormat,
    quality: u8,
) -> Result<Vec<u8>, ImgcError> {
    let mut out = Vec::new();
    match format {
        OutputFormat::Jpeg => {
            let rgb = img.to_rgb8();
            JpegEncoder::new_with_quality(&mut out, quality)
                .encode_image(&rgb)
                .map_err(|e| ImgcError::Encode(e.to_string()))?;
        }
        OutputFormat::Png => write_via_format(img, ImageFormat::Png, &mut out)?,
        OutputFormat::Tiff => write_via_format(img, ImageFormat::Tiff, &mut out)?,
        OutputFormat::WebP => {
            // image crate only ships a lossless WebP encoder.
            let rgba = img.to_rgba8();
            WebPEncoder::new_lossless(&mut out)
                .encode(
                    rgba.as_raw(),
                    rgba.width(),
                    rgba.height(),
                    ExtendedColorType::Rgba8,
                )
                .map_err(|e| ImgcError::Encode(e.to_string()))?;
        }
        OutputFormat::Pdf => return encode_pdf(img),
        OutputFormat::Ico | OutputFormat::Gif => unreachable!("handled in encode()"),
    }
    Ok(out)
}

fn write_via_format(
    img: &DynamicImage,
    format: ImageFormat,
    out: &mut Vec<u8>,
) -> Result<(), ImgcError> {
    img.write_to(&mut Cursor::new(out), format)
        .map_err(|e| ImgcError::Encode(e.to_string()))
}

fn encode_with_size(
    mut img: DynamicImage,
    format: OutputFormat,
    opts: &ConvertOptions,
) -> Result<Vec<u8>, ImgcError> {
    img = cap_dimensions(img, MAX_PIXEL_SIZE);
    let mut quality = START_QUALITY;
    let mut bytes = encode_once(&img, format, quality)?;

    if let Some(max_mb) = opts.max_size_mb {
        let max_bytes = mb_to_bytes(max_mb);
        let mut iter = 0;
        while bytes.len() > max_bytes && iter < SIZE_ITER_CAP {
            iter += 1;
            if format.is_lossy() && quality > MIN_QUALITY {
                quality = quality.saturating_sub(5).max(MIN_QUALITY);
            } else {
                let (w, h) = (img.width(), img.height());
                if w <= MIN_PIXEL_SIZE || h <= MIN_PIXEL_SIZE {
                    break;
                }
                img = img.resize(
                    (w * 9 / 10).max(1),
                    (h * 9 / 10).max(1),
                    image::imageops::FilterType::Lanczos3,
                );
            }
            bytes = encode_once(&img, format, quality)?;
        }
    }

    if let Some(min_mb) = opts.min_size_mb {
        let min_bytes = mb_to_bytes(min_mb);
        let mut iter = 0;
        while bytes.len() < min_bytes && iter < SIZE_ITER_CAP {
            iter += 1;
            let (w, h) = (img.width(), img.height());
            if w >= MAX_UPSCALE_SIZE || h >= MAX_UPSCALE_SIZE {
                break;
            }
            img = img.resize(
                w * 11 / 10,
                h * 11 / 10,
                image::imageops::FilterType::Lanczos3,
            );
            bytes = encode_once(&img, format, quality)?;
        }
    }

    Ok(bytes)
}

fn cap_dimensions(img: DynamicImage, max: u32) -> DynamicImage {
    let (w, h) = (img.width(), img.height());
    if w > max || h > max {
        img.resize(max, max, image::imageops::FilterType::Lanczos3)
    } else {
        img
    }
}

fn encode_ico(img: &DynamicImage, size: u32) -> Result<Vec<u8>, ImgcError> {
    // ICO frames are capped at 256px by the format.
    let size = size.clamp(1, 256);
    let resized = img.resize_exact(size, size, image::imageops::FilterType::Lanczos3);
    let mut out = Vec::new();
    resized
        .write_to(&mut Cursor::new(&mut out), ImageFormat::Ico)
        .map_err(|e| ImgcError::Encode(e.to_string()))?;
    Ok(out)
}

pub fn encode_animated_gif(
    frames: &[DynamicImage],
    opts: &ConvertOptions,
) -> Result<Vec<u8>, ImgcError> {
    if frames.is_empty() {
        return Err(ImgcError::NoFrames);
    }
    let fps = opts.fps.max(1);
    let delay = Delay::from_numer_denom_ms(1000, fps);
    let mut out = Vec::new();
    {
        let mut encoder = GifEncoder::new(&mut out);
        encoder
            .set_repeat(Repeat::Infinite)
            .map_err(|e| ImgcError::Encode(e.to_string()))?;
        for img in frames {
            let frame = Frame::from_parts(img.to_rgba8(), 0, 0, delay);
            encoder
                .encode_frame(frame)
                .map_err(|e| ImgcError::Encode(e.to_string()))?;
        }
    }
    Ok(out)
}

/// Wrap the image into a single-page PDF by embedding it as a JPEG (DCTDecode).
/// Hand-rolled so there is no PDF dependency and it behaves identically on wasm.
fn encode_pdf(img: &DynamicImage) -> Result<Vec<u8>, ImgcError> {
    let rgb = img.to_rgb8();
    let (w, h) = (rgb.width(), rgb.height());
    let mut jpeg = Vec::new();
    JpegEncoder::new_with_quality(&mut jpeg, 90)
        .encode_image(&rgb)
        .map_err(|e| ImgcError::Encode(e.to_string()))?;

    // Page is sized in points; 1px maps to 1pt (72 DPI).
    let content = format!("q {w} 0 0 {h} 0 0 cm /Im0 Do Q\n");

    let mut buf: Vec<u8> = b"%PDF-1.4\n".to_vec();
    let mut offsets = [0usize; 6];

    offsets[1] = buf.len();
    buf.extend_from_slice(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n");

    offsets[2] = buf.len();
    buf.extend_from_slice(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n");

    offsets[3] = buf.len();
    buf.extend_from_slice(
        format!(
            "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] \
             /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        )
        .as_bytes(),
    );

    offsets[4] = buf.len();
    buf.extend_from_slice(
        format!(
            "4 0 obj\n<< /Type /XObject /Subtype /Image /Width {w} /Height {h} \
             /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {} >>\nstream\n",
            jpeg.len()
        )
        .as_bytes(),
    );
    buf.extend_from_slice(&jpeg);
    buf.extend_from_slice(b"\nendstream\nendobj\n");

    offsets[5] = buf.len();
    buf.extend_from_slice(format!("5 0 obj\n<< /Length {} >>\nstream\n", content.len()).as_bytes());
    buf.extend_from_slice(content.as_bytes());
    buf.extend_from_slice(b"endstream\nendobj\n");

    let xref_pos = buf.len();
    buf.extend_from_slice(b"xref\n0 6\n0000000000 65535 f \n");
    for offset in &offsets[1..=5] {
        buf.extend_from_slice(format!("{offset:010} 00000 n \n").as_bytes());
    }
    buf.extend_from_slice(
        format!("trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n").as_bytes(),
    );

    Ok(buf)
}

fn mb_to_bytes(mb: f64) -> usize {
    (mb * 1024.0 * 1024.0).max(0.0) as usize
}
