import os

# import module
from pathlib import Path

from PIL import Image
from pdf2image import convert_from_path


def save(org_image: Image.Image,
         new_path: Path,
         max_size: float | None,
         min_size: float | None,
         min_quality: int = 95
         ):
    quality = 100
    old_size = 0
    optimize = True
    try:
        org_image.save(new_path, optimze=optimize, quality=quality)
    except:
        optimize = False
        org_image.save(new_path, optimze=optimize, quality=quality)
    image = org_image.copy()
    while min_size is not None:
        size = get_img_size(new_path)
        img_size = image.size
        if size < min_size:
            factor = (min_size / size) ** (1 / 2)
            new_size = (round(factor * img_size[0]), round(factor * img_size[1]))
            image = org_image.resize(new_size)
            image.save(new_path, optimze=optimize, quality=quality)
        else:
            min_size = None
    while max_size is not None:
        size = get_img_size(new_path)
        img_size = image.size
        quality -= 1
        if min_quality < quality:
            quality = min_quality
        if size > max_size:
            if old_size != size:
                old_size = size
                continue
            factor = (max_size / size) ** (1 / 2)
            new_size = (int(factor * img_size[0]), int(factor * img_size[1]))
            image = org_image.resize(new_size)
            image.save(new_path, optimze=optimize, quality=quality)
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


def load_images(img_folder: Path, filter_suffix: str):
    images = []
    for img_path in img_folder.glob("*"):
        if filter_suffix is not None:
            if img_path.suffix != filter_suffix:
                continue
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
        dpi = 1200
        while True:
            try:
                pdfs = convert_from_path(img_path, dpi=dpi)
            except:
                dpi -= 200
                continue
            break
        if len(pdfs) == 1:
            return (pdfs[0], Path(str(img_path).replace(img_path.suffix, ".pdf")))
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
