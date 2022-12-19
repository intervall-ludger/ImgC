import os
import unittest
from pathlib import Path

from PIL import Image

from imgC import convert, load_image, load_images, save

base_path = Path(__file__).parent


def generate_test_data():
    # Create test data folder if it doesn't exist
    test_data_folder = base_path / "test_data"
    if not test_data_folder.exists():
        test_data_folder.mkdir()

    # Create test image
    test_image = Image.new("RGB", (500, 500), "white")
    test_image.save(base_path / "test_data/test_image.jpg")


class TestImgc(unittest.TestCase):
    def setUp(self) -> None:
        generate_test_data()

    def test_convert(self):
        # Test converting a single image
        img_path = base_path / "test_data/test_image.jpg"
        convert(img_path, "png", max_size=0.1, min_size=0.05)
        self.assertTrue(img_path.with_suffix(".png").exists())

        # Test converting a folder of images
        img_folder = base_path / "test_data"
        convert(img_folder, "jpg", max_size=0.1, min_size=0.05)
        for img_path in img_folder.glob("*.jpg"):
            self.assertTrue(img_path.exists())

        # Test converting with a specified input suffix
        convert(img_folder, "tif", filter_suffix="jpg", max_size=0.1, min_size=0.05)
        for img_path in img_folder.glob("*.tif"):
            self.assertTrue(img_path.exists())

        # Test converting with no size constraints
        convert(img_folder, "pdf", filter_suffix="tif")
        for img_path in img_folder.glob("*.pdf"):
            self.assertTrue(img_path.exists())


if __name__ == "__main__":
    unittest.main()
