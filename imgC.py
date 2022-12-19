from support_function import *
import argparse


def convert(img_path: Path,
            out_suffix: str,
            max_size: float | None,
            min_size: float | None,
            filter_suffix: str | None = None):
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
        print(f'Invalid input path: {img_path}')
        return None
    for image, filename in images:
        if image is None:
            continue
        if out_suffix == "jpg":
            save_jpg(image, filename, max_size, min_size)
        elif out_suffix == "png":
            save_png(image, filename, max_size, min_size)
        elif out_suffix == "tif":
            save_tif(image, filename, max_size, min_size)
        elif out_suffix == "pdf":
            save_pdf(image, filename, max_size, min_size)
        else:
            raise NotImplementedError


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="ImgC - Optimizer for image format and size"
    )
    parser.add_argument(
        "-f", "--filename", type=Path, help="Image file or folder with images"
    )
    parser.add_argument(
        "--filter_suffix",
        type=str,
        default='*',
        help="Suffix of the input image. (Optional)",
    )
    parser.add_argument(
        "-s",
        "--suffix",
        type=str,
        help="Suffix of the output image. "
        "Currently implemented: 'png', 'jpg', 'tif', 'pdf'",
    )
    parser.add_argument("--min", type=float, help="max image size in MB", default=None)
    parser.add_argument("--max", type=float, help="max image size in MB", default=None)

    args = parser.parse_args()
    convert(args.filename, args.suffix, args.max, args.min)
