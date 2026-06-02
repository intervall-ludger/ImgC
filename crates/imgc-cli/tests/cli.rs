use std::path::{Path, PathBuf};
use std::process::Command;

fn imgc() -> Command {
    Command::new(env!("CARGO_BIN_EXE_imgc"))
}

fn fixture(name: &str) -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures")
        .join(name)
}

fn make_png(path: &Path, w: u32, h: u32) {
    image::RgbImage::from_fn(w, h, |x, y| {
        image::Rgb([(x % 256) as u8, (y % 256) as u8, 128])
    })
    .save(path)
    .unwrap();
}

fn starts_with(path: &Path, signature: &[u8]) -> bool {
    std::fs::read(path).unwrap().starts_with(signature)
}

#[test]
fn converts_png_to_every_format() {
    let dir = tempfile::tempdir().unwrap();
    let src = dir.path().join("input.png");
    make_png(&src, 64, 64);

    // (format flag, output extension, magic-byte signature)
    let cases: &[(&str, &str, &[u8])] = &[
        ("png", "png", &[0x89, 0x50, 0x4E, 0x47]),
        ("jpg", "jpg", &[0xFF, 0xD8, 0xFF]),
        ("tif", "tif", &[0x49, 0x49, 0x2A, 0x00]),
        ("gif", "gif", b"GIF"),
        ("ico", "ico", &[0x00, 0x00, 0x01, 0x00]),
        ("webp", "webp", b"RIFF"),
        ("pdf", "pdf", b"%PDF"),
    ];

    for (format, ext, signature) in cases {
        let status = imgc()
            .args(["-f", src.to_str().unwrap(), "-s", format])
            .status()
            .unwrap();
        assert!(status.success(), "cli exited non-zero for {format}");

        let out = src.with_extension(ext);
        assert!(out.exists(), "{format}: output file missing");
        assert!(starts_with(&out, signature), "{format}: wrong magic bytes");
    }
}

#[test]
fn converts_real_dicom_to_png() {
    // Real 16-bit MONOCHROME2 CT scan (see tests/fixtures/README.md).
    let dir = tempfile::tempdir().unwrap();
    let src = dir.path().join("ct.dcm");
    std::fs::copy(fixture("ct_small.dcm"), &src).unwrap();

    let status = imgc()
        .args(["-f", src.to_str().unwrap(), "-s", "png"])
        .status()
        .unwrap();
    assert!(status.success(), "dicom conversion exited non-zero");

    let out = src.with_extension("png");
    assert!(out.exists(), "dicom: png output missing");
    assert!(starts_with(&out, &[0x89, 0x50, 0x4E, 0x47]));
}

#[test]
fn folder_of_stills_becomes_animated_gif() {
    let dir = tempfile::tempdir().unwrap();
    let frames = dir.path().join("frames");
    std::fs::create_dir(&frames).unwrap();
    for i in 0..4 {
        make_png(&frames.join(format!("frame_{i}.png")), 32, 32);
    }

    let status = imgc()
        .args([
            "-f",
            frames.to_str().unwrap(),
            "-s",
            "gif",
            "--fps",
            "5",
            "--filter_suffix",
            "png",
        ])
        .status()
        .unwrap();
    assert!(status.success(), "gif conversion exited non-zero");

    // The folder of stills is written as a sibling <folder>.gif.
    let gif = frames.with_extension("gif");
    assert!(gif.exists(), "animated gif missing at {gif:?}");
    assert!(starts_with(&gif, b"GIF"));
}

#[test]
fn max_size_flag_shrinks_jpeg() {
    let dir = tempfile::tempdir().unwrap();
    let src = dir.path().join("big.png");
    make_png(&src, 1500, 1500);

    let status = imgc()
        .args(["-f", src.to_str().unwrap(), "-s", "jpg", "--max", "0.05"])
        .status()
        .unwrap();
    assert!(status.success());

    let out = src.with_extension("jpg");
    let size = std::fs::metadata(&out).unwrap().len();
    assert!(size <= 64 * 1024, "expected <= 64KB, got {size} bytes");
}

#[cfg(feature = "heic")]
#[test]
fn converts_heic_to_png() {
    let dir = tempfile::tempdir().unwrap();
    let src = dir.path().join("photo.heic");
    std::fs::copy(fixture("sample.heic"), &src).unwrap();

    let status = imgc()
        .args(["-f", src.to_str().unwrap(), "-s", "png"])
        .status()
        .unwrap();
    assert!(status.success(), "heic conversion exited non-zero");

    let out = src.with_extension("png");
    assert!(out.exists(), "heic: png output missing");
    assert!(starts_with(&out, &[0x89, 0x50, 0x4E, 0x47]));
}

#[test]
fn rejects_unknown_output_format() {
    let dir = tempfile::tempdir().unwrap();
    let src = dir.path().join("x.png");
    make_png(&src, 8, 8);

    let status = imgc()
        .args(["-f", src.to_str().unwrap(), "-s", "xyz"])
        .status()
        .unwrap();
    assert!(!status.success(), "unknown format should fail");
}
