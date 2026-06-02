use imgc_core::{convert_frames, convert_image, ConvertOptions, OutputFormat};
use wasm_bindgen::prelude::*;

#[wasm_bindgen(start)]
pub fn start() {
    console_error_panic_hook::set_once();
}

fn parse_format(format: &str) -> Result<OutputFormat, JsError> {
    OutputFormat::from_extension(format)
        .ok_or_else(|| JsError::new(&format!("unsupported output format: {format}")))
}

/// Convert a single encoded image into the target format. Returns the encoded bytes.
#[wasm_bindgen]
pub fn convert(
    input: &[u8],
    format: &str,
    max_mb: Option<f64>,
    min_mb: Option<f64>,
    fps: u32,
    icon_size: u32,
) -> Result<Vec<u8>, JsError> {
    let opts = ConvertOptions {
        max_size_mb: max_mb,
        min_size_mb: min_mb,
        fps,
        icon_size,
    };
    convert_image(input, parse_format(format)?, &opts).map_err(|e| JsError::new(&e.to_string()))
}

/// Combine multiple encoded images into a single animated GIF.
#[wasm_bindgen]
pub fn convert_to_gif(frames: js_sys::Array, fps: u32) -> Result<Vec<u8>, JsError> {
    let inputs: Vec<Vec<u8>> = frames
        .iter()
        .map(|v| js_sys::Uint8Array::new(&v).to_vec())
        .collect();
    let opts = ConvertOptions {
        fps,
        ..Default::default()
    };
    convert_frames(&inputs, &opts).map_err(|e| JsError::new(&e.to_string()))
}
