import os

# import module
from pathlib import Path
from typing import Tuple

import PIL.Image
import imageio
import natsort
import numpy as np
import pydicom
from PIL import Image, ImageFilter

from pdf2image import convert_from_path


def save(
    org_image: Image.Image,
    new_path: Path,
    max_size: float | None,
    min_size: float | None,
    min_quality: int = 95,
    max_pixel_size: int = 8000,
) -> None:
    quality = 100
    old_size = 0
    optimize = True
    # Save the original image to the new path
    # If optimization fails, try saving again without optimization
    img_size = org_image.size
    if img_size[0] > max_pixel_size or img_size[1] > max_pixel_size:
        if img_size[0] > max_pixel_size:
            img_size = (
                max_pixel_size,
                int(img_size[1] / (img_size[0] / max_pixel_size)),
            )
        else:
            img_size = (
                int(img_size[0] / (img_size[1] / max_pixel_size)),
                max_pixel_size,
            )
        org_image = org_image.resize(img_size)

    try:
        org_image.save(new_path, optimze=optimize, quality=quality)
    except:
        optimize = False
        org_image.save(new_path, optimze=optimize, quality=quality)
    image = org_image.copy()
    # If a minimum size is specified, resize the image until it meets the minimum size requirement
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

    # If a maximum size is specified, resize the image and reduce the quality until
    # it meets the maximum size requirement
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


def save_jpg(
    image: Image.Image, img_path: Path, max_size: float | None, min_size: float | None
) -> None:
    image = image.convert("RGB")
    save(image, img_path.with_suffix(".jpg"), max_size, min_size)


def save_png(
    image: Image.Image, img_path: Path, max_size: float | None, min_size: float | None
) -> None:
    save(image, img_path.with_suffix(".png"), max_size, min_size)


def save_ico(image, filename, size: int = 64):
    # Convert the image to RGB
    image = image.convert("RGB")

    # Resize the image using high-quality resampling
    image = image.resize((size, size), Image.BICUBIC)

    # Apply sharpening filter
    sharper = ImageFilter.SHARPEN()
    image = image.filter(sharper)

    # Save the image in ICO format
    image.save(filename.with_suffix(".ico"), format="ICO", size=(size, size))


def save_tif(
    image: Image.Image, img_path: Path, max_size: float | None, min_size: float | None
) -> None:
    save(image, img_path.with_suffix(".tif"), max_size, min_size)


def save_pdf(
    image: Image.Image, img_path: Path, max_size: float | None, min_size: float | None
) -> None:
    image = image.convert("RGB")
    save(image, img_path.with_suffix(".pdf"), max_size, min_size)


def save_mp4(images: list[Image.Image], video_path: Path, fps: int) -> None:
    imageio.mimsave(video_path.with_suffix(".mp4"), images, fps=fps)  # save as mp4


def save_gif(
    images: list[Image.Image], gif_path: Path, fps: int, max_size: int
) -> None:
    def resize_image(image: Image, max_size: int) -> Image:
        ratio = max_size / max(image.size)
        new_size = tuple([int(x * ratio) for x in image.size])
        resized_image = image.resize(new_size, Image.ANTIALIAS)
        return resized_image

    if images[0].size[0] > max_size or images[0].size[1] > max_size:
        images = [resize_image(_, max_size) for _ in images]
    imageio.mimsave(
        gif_path.with_suffix(".gif"), images[:: int(60 / fps)], duration=int(1000 / fps)
    )  # save as gif


def load_images(img_folder: Path, filter_suffix: str) -> list[PIL.Image.Image]:
    images = []
    for img_path in natsort.natsorted(img_folder.glob("*")):
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


def load_image(img_path: Path) -> Tuple:
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
    elif img_path.suffix in [".jpg", ".png", ".tif"]:
        return Image.open(img_path), img_path
    elif img_path.suffix == ".dcm":  # handle dicom files
        dicom = pydicom.dcmread(str(img_path))
        array = dicom.pixel_array

        # Scale image to the range 0-255
        array = array - array.min()
        array = array / array.max()
        array = (array * 255).astype(np.uint8)

        array = np.stack((array,) * 3, axis=-1)

        # Create a PIL image
        image = Image.fromarray(array, "RGB")

        return image, img_path
    elif img_path.suffix in [".gif", ".mp4"]:
        output = []
        reader = imageio.get_reader(img_path)
        for i, img in enumerate(reader):
            pil_img = Image.fromarray(img)
            output.append(
                (
                    pil_img,
                    Path(
                        str(img_path).replace(img_path.suffix, f"_{i}{img_path.suffix}")
                    ),
                )
            )
        return output
    return None, ""


# Convert a string representation of bytes to megabytes
# and return the result as a float
def bytes_to_MB(bytes: str) -> float:
    # Divide the number of bytes by the number of bytes in a megabyte
    # (1024 bytes in a kilobyte and 1024 kilobytes in a megabyte)
    # and return the result as a float
    return float(bytes) / (1024**2)


# Get the size of an image file in megabytes
def get_img_size(img_path: Path):
    # Use the os module's getsize function to get the size of the image file
    # in bytes and pass it to the bytes_to_MB function to convert it to megabytes
    return bytes_to_MB(os.path.getsize(img_path))
