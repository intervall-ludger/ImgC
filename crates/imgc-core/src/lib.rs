mod encode;
mod load;

pub use encode::OutputFormat;

use thiserror::Error;

#[derive(Debug, Error)]
pub enum ImgcError {
    #[error("failed to decode input image: {0}")]
    Decode(String),
    #[error("failed to encode output image: {0}")]
    Encode(String),
    #[error("unsupported DICOM file: {0}")]
    Dicom(String),
    #[error("no frames provided")]
    NoFrames,
}

#[derive(Debug, Clone)]
pub struct ConvertOptions {
    pub max_size_mb: Option<f64>,
    pub min_size_mb: Option<f64>,
    pub fps: u32,
    pub icon_size: u32,
}

impl Default for ConvertOptions {
    fn default() -> Self {
        Self {
            max_size_mb: None,
            min_size_mb: None,
            fps: 30,
            icon_size: 64,
        }
    }
}

/// Convert a single encoded image (any supported input, incl. DICOM) into the target format.
pub fn convert_image(
    input: &[u8],
    format: OutputFormat,
    opts: &ConvertOptions,
) -> Result<Vec<u8>, ImgcError> {
    let img = load::load(input)?;
    encode::encode(img, format, opts)
}

/// Combine multiple encoded images into a single animated GIF.
pub fn convert_frames(inputs: &[Vec<u8>], opts: &ConvertOptions) -> Result<Vec<u8>, ImgcError> {
    if inputs.is_empty() {
        return Err(ImgcError::NoFrames);
    }
    let frames = inputs
        .iter()
        .map(|bytes| load::load(bytes))
        .collect::<Result<Vec<_>, _>>()?;
    encode::encode_animated_gif(&frames, opts)
}

#[cfg(test)]
mod tests {
    use super::*;
    use image::{DynamicImage, ImageFormat, RgbImage};
    use std::io::Cursor;

    fn sample_png(w: u32, h: u32) -> Vec<u8> {
        let img = RgbImage::from_fn(w, h, |x, y| {
            image::Rgb([(x % 256) as u8, (y % 256) as u8, 128])
        });
        let mut out = Vec::new();
        DynamicImage::ImageRgb8(img)
            .write_to(&mut Cursor::new(&mut out), ImageFormat::Png)
            .unwrap();
        out
    }

    #[test]
    fn converts_to_every_single_image_format() {
        let input = sample_png(200, 150);
        let opts = ConvertOptions::default();
        for format in [
            OutputFormat::Png,
            OutputFormat::Jpeg,
            OutputFormat::Tiff,
            OutputFormat::Gif,
            OutputFormat::Ico,
            OutputFormat::WebP,
            OutputFormat::Pdf,
        ] {
            let out = convert_image(&input, format, &opts).expect("conversion failed");
            assert!(!out.is_empty(), "{format:?} produced no bytes");
        }
    }

    #[test]
    fn max_size_shrinks_output() {
        let input = sample_png(2000, 2000);
        let opts = ConvertOptions {
            max_size_mb: Some(0.05),
            ..Default::default()
        };
        let out = convert_image(&input, OutputFormat::Jpeg, &opts).unwrap();
        assert!(out.len() <= (0.05 * 1024.0 * 1024.0) as usize * 2);
    }

    #[test]
    fn animated_gif_from_frames() {
        let frames = vec![sample_png(64, 64), sample_png(64, 64), sample_png(64, 64)];
        let opts = ConvertOptions {
            fps: 10,
            ..Default::default()
        };
        let gif = convert_frames(&frames, &opts).unwrap();
        assert_eq!(
            image::guess_format(&gif).unwrap(),
            ImageFormat::Gif,
            "output is not a gif"
        );
    }

    #[test]
    fn rejects_garbage_input() {
        let err = convert_image(
            b"not an image",
            OutputFormat::Png,
            &ConvertOptions::default(),
        );
        assert!(err.is_err());
    }
}
