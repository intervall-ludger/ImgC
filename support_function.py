import os

# import module
from pathlib import Path

from PIL import Image
from pdf2image import convert_from_path


def save(image: Image.Image,
         new_path: Path,
         max_size: float | None,
         min_size: float | None
         ):
    quality = 100
    old_size = 0
    image.save(new_path, optimze=True, quality=quality)

    while min_size is not None:
        size = get_img_size(new_path)
        img_size = image.size
        if size < min_size:
            factor = (min_size / size) ** (1 / 2)
            new_size = (round(factor * img_size[0]), round(factor * img_size[1]))
            image = image.resize(new_size)
            image.save(new_path, optimze=True, quality=quality)
        else:
            min_size = None
    while max_size is not None:
        size = get_img_size(new_path)
        img_size = image.size
        quality -= 1
        if size > max_size:
            if old_size != size:
                old_size = size
                continue
            factor = (max_size / size) ** (1 / 2)
            new_size = (int(factor * img_size[0]), int(factor * img_size[1]))
            image = image.resize(new_size)
            image.save(new_path, optimze=True, quality=quality)
        else:
            max_size = None


def save_jpg(image: Image.Image,
             img_path: Path,
             max_size: float | None,
             min_size: float | None
             ):
    image = image.convert("RGB")
    save(image, img_path.with_suffix(".jpg"), max_size, min_size)


def save_png(image: Image.Image,
             img_path: Path,
             max_size: float | None,
             min_size: float | None):
    save(image, img_path.with_suffix(".png"), max_size, min_size)


def save_tif(image: Image.Image,
             img_path: Path,
             max_size: float | None,
             min_size: float | None):
    save(image, img_path.with_suffix(".tif"), max_size, min_size)


def save_pdf(image: Image.Image,
             img_path: Path,
             max_size: float | None,
             min_size: float | None):
    image = image.convert("RGB")
    save(image, img_path.with_suffix(".pdf"), max_size, min_size)


def load_images(img_folder: Path):
    images = []
    for img_path in img_folder.glob("*"):
        output = load_image(img_path)
        if type(output) == list:
            for img_tuple in output:
                images.append(img_tuple)
        else:
            images.append(output)
    return images


def load_image(img_path: Path):
    if img_path.suffix == ".pdf":
        output = []
        pdfs = convert_from_path(img_path)
        for i, pdf in enumerate(pdfs):
            output.append(
                (pdf, Path(str(img_path).replace(img_path.suffix, f"_{i}.pdf")))
            )
        return output
    if img_path.suffix in [".png"]:
        return Image.open(img_path), img_path
    return None, ""


def bytes_to_MB(bytes: str):
    return float(bytes) / (1024 ** 2)


def get_img_size(img_path: Path):
    return bytes_to_MB(os.path.getsize(img_path))
