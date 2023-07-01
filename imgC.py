import argparse

from support_function import *


def convert(
    img_path: Path,
    out_suffix: str,
    max_size: float | None = None,
    min_size: float | None = None,
    filter_suffix: str | None = None,
    fps: int = 30,
    size: int = 64,
):
    if filter_suffix == "*":
        filter_suffix = None
    try:
        if img_path.is_dir():
            images = load_images(img_path, filter_suffix)
        else:
            if filter_suffix is not None:
                if img_path.suffix != filter_suffix:
                    raise RuntimeError
            images = load_image(img_path)
            if type(images) == tuple:
                images = [images]
    except AttributeError as e:
        print(f"Invalid input path: {img_path}")
        return None
    if out_suffix in [".mp4", ".gif"]:
        # Save as mp4 or gif if multiple images are found
        image_list = [img_tuple[0] for img_tuple in images]
        if out_suffix == ".mp4":
            if filter_suffix not in [".mp4", ".gif"]:
                save_mp4(image_list, img_path.with_name(img_path.stem), fps)
            else:
                save_mp4(image_list, images[0][1].parent / images[0][1].name.split('_')[-2], fps)
        else:
            if filter_suffix not in [".mp4", ".gif"]:
                save_gif(image_list, img_path.with_name(img_path.stem), fps)
            else:
                save_gif(image_list, images[0][1].parent / images[0][1].name.split('_')[-2], fps, max_size=size)
    else:
        for image, filename in images:
            if image is None:
                continue
            if out_suffix == ".jpg":
                save_jpg(image, filename, max_size, min_size)
            elif out_suffix == ".png":
                save_png(image, filename, max_size, min_size)
            elif out_suffix == ".tif":
                save_tif(image, filename, max_size, min_size)
            elif out_suffix == ".pdf":
                save_pdf(image, filename, max_size, min_size)
            elif out_suffix == ".ico":
                save_ico(image, filename, size=size)
            else:
                raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ImgC - Optimizer for image format and size"
    )
    parser.add_argument(
        "-f", "--filename", type=Path, help="Image file or folder with images"
    )
    parser.add_argument(
        "--filter_suffix",
        type=str,
        default="*",
        help="Suffix of the input image. (Optional)",
    )
    parser.add_argument(
        "-s",
        "--suffix",
        type=str,
        help="Suffix of the output image. "
        "Currently implemented: 'png', 'jpg', 'tif', 'pdf', 'mp4', 'gif', 'ico', 'mp4', 'gif'",
    )
    parser.add_argument(
        "--min", type=float, help="Minimum image size in MB", default=None
    )
    parser.add_argument(
        "--max", type=float, help="Maximum image size in MB", default=None
    )
    parser.add_argument(
        "--fps", type=int, help="Frames per second for video output", default=30
    )
    parser.add_argument("--size", type=int, help="Icon size for ICO output", default=64)

    args = parser.parse_args()
    args.suffix = args.suffix if "." in args.suffix else f".{args.suffix}"
    args.filter_suffix = (
        args.filter_suffix if "." in args.filter_suffix else f".{args.filter_suffix}"
    )
    convert(
        args.filename,
        args.suffix,
        args.max,
        args.min,
        args.filter_suffix,
        args.fps,
        args.size,
    )
