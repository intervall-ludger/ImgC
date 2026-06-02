use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use clap::Parser;
use imgc_core::{convert_frames, convert_image, ConvertOptions, OutputFormat};

#[derive(Parser)]
#[command(
    name = "imgc",
    version,
    about = "ImgC - optimize image format and size"
)]
struct Cli {
    /// Image file or folder of images to convert
    #[arg(short = 'f', long)]
    filename: PathBuf,

    /// Output format: png, jpg, tif, gif, ico, webp, pdf
    #[arg(short = 's', long)]
    suffix: String,

    /// Only process inputs with this extension (folder mode). Omit for all
    #[arg(long = "filter_suffix", visible_alias = "filter-suffix")]
    filter_suffix: Option<String>,

    /// Maximum output size in MB
    #[arg(long)]
    max: Option<f64>,

    /// Minimum output size in MB
    #[arg(long)]
    min: Option<f64>,

    /// Frames per second for animated GIF output
    #[arg(long, default_value_t = 30)]
    fps: u32,

    /// Pixel size for ICO output
    #[arg(long, default_value_t = 64)]
    size: u32,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match run(&cli) {
        Ok(count) => {
            println!("Done. {count} file(s) written.");
            ExitCode::SUCCESS
        }
        Err(msg) => {
            eprintln!("Error: {msg}");
            ExitCode::FAILURE
        }
    }
}

fn run(cli: &Cli) -> Result<usize, String> {
    let format = OutputFormat::from_extension(&cli.suffix)
        .ok_or_else(|| format!("unsupported output format: {}", cli.suffix))?;
    let opts = ConvertOptions {
        max_size_mb: cli.max,
        min_size_mb: cli.min,
        fps: cli.fps,
        icon_size: cli.size,
    };
    let filter = cli.filter_suffix.as_deref().filter(|s| *s != "*");

    if cli.filename.is_dir() {
        convert_dir(&cli.filename, format, &opts, filter)
    } else {
        convert_single(&cli.filename, format, &opts)
    }
}

fn convert_dir(
    dir: &Path,
    format: OutputFormat,
    opts: &ConvertOptions,
    filter: Option<&str>,
) -> Result<usize, String> {
    let mut inputs: Vec<PathBuf> = fs::read_dir(dir)
        .map_err(|e| e.to_string())?
        .filter_map(|entry| entry.ok().map(|e| e.path()))
        .filter(|p| p.is_file() && matches_filter(p, filter))
        .collect();
    inputs.sort();

    if inputs.is_empty() {
        return Err("no matching input files found".into());
    }

    if format == OutputFormat::Gif {
        // A folder of stills becomes a single animated GIF named after the folder.
        let frames = inputs
            .iter()
            .map(fs::read)
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| e.to_string())?;
        let gif = convert_frames(&frames, opts).map_err(|e| e.to_string())?;
        let out_path = dir.with_extension("gif");
        fs::write(&out_path, gif).map_err(|e| e.to_string())?;
        println!("{} -> {}", dir.display(), out_path.display());
        return Ok(1);
    }

    let mut count = 0;
    for path in &inputs {
        match convert_single(path, format, opts) {
            Ok(n) => count += n,
            Err(e) => eprintln!("skip {}: {e}", path.display()),
        }
    }
    Ok(count)
}

fn convert_single(
    path: &Path,
    format: OutputFormat,
    opts: &ConvertOptions,
) -> Result<usize, String> {
    let input = fs::read(path).map_err(|e| e.to_string())?;
    let output = convert_image(&input, format, opts).map_err(|e| e.to_string())?;
    let out_path = path.with_extension(format.extension());
    fs::write(&out_path, output).map_err(|e| e.to_string())?;
    println!("{} -> {}", path.display(), out_path.display());
    Ok(1)
}

fn matches_filter(path: &Path, filter: Option<&str>) -> bool {
    match filter {
        None => true,
        Some(want) => {
            let want = want.trim_start_matches('.').to_ascii_lowercase();
            path.extension()
                .and_then(|e| e.to_str())
                .map(|e| e.to_ascii_lowercase() == want)
                .unwrap_or(false)
        }
    }
}
