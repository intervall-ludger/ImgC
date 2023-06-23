import os
import unittest
from pathlib import Path

from PIL import Image

from imgC import convert, load_image, load_images, save

base_path = Path(__file__).parent


def generate_test_data():
    # Create test data folder if it doesn't exist
    test_data_folder = base_path / "test_data" / "images"
    if not test_data_folder.exists():
        test_data_folder.mkdir(parents=True)

    # Create multiple test images
    for i in range(10):
        test_image = Image.new("RGB", (500, 500), color=(i * 25, i * 25, i * 25))
        test_image.save(base_path / f"test_data/images/test_image_{i}.jpg")


class TestImgc(unittest.TestCase):
    def setUp(self) -> None:
        generate_test_data()

    def test_convert(self):
        # Test converting a single image
        img_path = base_path / "test_data/images/test_image_1.jpg"
        convert(img_path, ".png", max_size=0.1, min_size=0.05)
        self.assertTrue(img_path.with_suffix(".png").exists())

        # Test converting a single image to ico
        img_path = base_path / "test_data/images/test_image_1.jpg"
        convert(img_path, ".ico", size=128)
        self.assertTrue(img_path.with_suffix(".ico").exists())

        img_folder = base_path / "test_data/images"

        # Test converting a folder of images to mp4
        convert(img_folder, ".mp4", fps=30, filter_suffix=".jpg")
        self.assertTrue((Path(f"{img_folder}.mp4")).exists())

        # Test converting with a specified input suffix
        convert(img_folder, ".tif", filter_suffix=".jpg", max_size=1, min_size=0.5)
        for img_path in img_folder.glob("*.tif"):
            self.assertTrue(img_path.exists())

        # Test converting with no size constraints
        convert(img_folder, ".pdf", filter_suffix=".tif")
        for img_path in img_folder.glob("*.pdf"):
            self.assertTrue(img_path.exists())


if __name__ == "__main__":
    unittest.main()
