use crate::ImgcError;
use dicom_pixeldata::PixelDecoder;
use image::DynamicImage;

const DICOM_MAGIC: &[u8] = b"DICM";
const DICOM_PREAMBLE_LEN: usize = 128;

pub fn load(input: &[u8]) -> Result<DynamicImage, ImgcError> {
    #[cfg(feature = "heic")]
    if is_heic(input) {
        return load_heic(input);
    }
    if is_dicom(input) {
        load_dicom(input)
    } else {
        image::load_from_memory(input).map_err(|e| ImgcError::Decode(e.to_string()))
    }
}

fn is_dicom(input: &[u8]) -> bool {
    input.len() > DICOM_PREAMBLE_LEN + DICOM_MAGIC.len()
        && &input[DICOM_PREAMBLE_LEN..DICOM_PREAMBLE_LEN + DICOM_MAGIC.len()] == DICOM_MAGIC
}

fn load_dicom(input: &[u8]) -> Result<DynamicImage, ImgcError> {
    // from_reader detects and skips the preamble + "DICM" marker itself, so feed the full file.
    let obj = dicom_object::from_reader(input).map_err(|e| ImgcError::Dicom(e.to_string()))?;
    let decoded = obj
        .decode_pixel_data()
        .map_err(|e| ImgcError::Dicom(e.to_string()))?;
    decoded
        .to_dynamic_image(0)
        .map_err(|e| ImgcError::Dicom(e.to_string()))
}

#[cfg(feature = "heic")]
const HEIC_BRANDS: &[&[u8]] = &[
    b"heic", b"heix", b"heim", b"heis", b"hevc", b"hevx", b"mif1", b"msf1", b"heif",
];

#[cfg(feature = "heic")]
fn is_heic(input: &[u8]) -> bool {
    // HEIC is ISO-BMFF: the file starts with an `ftyp` box whose major brand
    // identifies the variant.
    input.len() >= 12 && &input[4..8] == b"ftyp" && HEIC_BRANDS.contains(&&input[8..12])
}

#[cfg(feature = "heic")]
fn load_heic(input: &[u8]) -> Result<DynamicImage, ImgcError> {
    use libheif_rs::{ColorSpace, HeifContext, LibHeif, RgbChroma};

    let lib = LibHeif::new();
    let ctx = HeifContext::read_from_bytes(input).map_err(|e| ImgcError::Decode(e.to_string()))?;
    let handle = ctx
        .primary_image_handle()
        .map_err(|e| ImgcError::Decode(e.to_string()))?;
    let decoded = lib
        .decode(&handle, ColorSpace::Rgb(RgbChroma::Rgb), None)
        .map_err(|e| ImgcError::Decode(e.to_string()))?;

    let width = decoded.width();
    let height = decoded.height();
    let planes = decoded.planes();
    let plane = planes
        .interleaved
        .ok_or_else(|| ImgcError::Decode("HEIC frame has no interleaved RGB plane".into()))?;

    // The decoded plane is padded to `stride` bytes per row; copy the tight rows out.
    let row_bytes = width as usize * 3;
    let mut buf = Vec::with_capacity(row_bytes * height as usize);
    for y in 0..height as usize {
        let start = y * plane.stride;
        buf.extend_from_slice(&plane.data[start..start + row_bytes]);
    }

    let rgb = image::RgbImage::from_raw(width, height, buf)
        .ok_or_else(|| ImgcError::Decode("HEIC pixel buffer size mismatch".into()))?;
    Ok(DynamicImage::ImageRgb8(rgb))
}

#[cfg(test)]
mod tests {
    use crate::{convert_image, ConvertOptions, OutputFormat};
    use dicom_core::{DataElement, PrimitiveValue, VR};
    use dicom_dictionary_std::tags;
    use dicom_object::{FileMetaTableBuilder, InMemDicomObject};

    // Build a minimal uncompressed 4x4 MONOCHROME2 DICOM in memory (with preamble + "DICM").
    fn synthetic_dicom() -> Vec<u8> {
        let mut obj = InMemDicomObject::new_empty();
        let put = |obj: &mut InMemDicomObject, tag, vr, value: PrimitiveValue| {
            obj.put(DataElement::new(tag, vr, value));
        };
        put(
            &mut obj,
            tags::SAMPLES_PER_PIXEL,
            VR::US,
            PrimitiveValue::from(1u16),
        );
        put(
            &mut obj,
            tags::PHOTOMETRIC_INTERPRETATION,
            VR::CS,
            PrimitiveValue::from("MONOCHROME2"),
        );
        put(&mut obj, tags::ROWS, VR::US, PrimitiveValue::from(4u16));
        put(&mut obj, tags::COLUMNS, VR::US, PrimitiveValue::from(4u16));
        put(
            &mut obj,
            tags::BITS_ALLOCATED,
            VR::US,
            PrimitiveValue::from(8u16),
        );
        put(
            &mut obj,
            tags::BITS_STORED,
            VR::US,
            PrimitiveValue::from(8u16),
        );
        put(&mut obj, tags::HIGH_BIT, VR::US, PrimitiveValue::from(7u16));
        put(
            &mut obj,
            tags::PIXEL_REPRESENTATION,
            VR::US,
            PrimitiveValue::from(0u16),
        );
        let pixels: Vec<u8> = (0..16u8).map(|i| i * 16).collect();
        put(
            &mut obj,
            tags::PIXEL_DATA,
            VR::OB,
            PrimitiveValue::from(pixels),
        );

        let meta = FileMetaTableBuilder::new()
            .media_storage_sop_class_uid("1.2.840.10008.5.1.4.1.1.7")
            .media_storage_sop_instance_uid("1.2.3.4.5")
            .transfer_syntax("1.2.840.10008.1.2.1")
            .implementation_class_uid("1.2.3.4");

        let mut bytes = Vec::new();
        obj.with_meta(meta).unwrap().write_all(&mut bytes).unwrap();
        bytes
    }

    #[test]
    fn loads_and_converts_dicom() {
        let dcm = synthetic_dicom();
        let out = convert_image(&dcm, OutputFormat::Png, &ConvertOptions::default())
            .expect("DICOM conversion failed");
        assert_eq!(image::guess_format(&out).unwrap(), image::ImageFormat::Png);
    }
}
