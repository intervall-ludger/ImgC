import os
import unittest
from pathlib import Path

from PIL import Image

from imgC import convert, load_image, load_images, save

base_path = Path(__file__).parent

def generate_test_data():
    # Create test data folder if it doesn't exist
    test_data_folder = base_path / 'test_data'
    if not test_data_folder.exists():
        test_data_folder.mkdir()

    # Create test image
    test_image = Image.new('RGB', (500, 500), 'white')
    test_image.save(base_path / 'test_data/test_image.jpg')

    # Create invalid image
    with open(base_path / 'test_data/invalid_image.jpg', 'w') as f:
        f.write('invalid image')



class TestImgc(unittest.TestCase):

    def test_convert(self):
        # Test converting a single image
        img_path = base_path / 'test_data/test_image.jpg'
        convert(img_path, 'png', max_size=1, min_size=0.5)
        self.assertTrue(img_path.with_suffix('.png').exists())

        # Test converting a folder of images
        img_folder = base_path / 'test_data'
        convert(img_folder, 'jpg', max_size=1, min_size=0.5)
        for img_path in img_folder.glob('*.jpg'):
            self.assertTrue(img_path.exists())

        # Test converting with a specified input suffix
        convert(img_folder, 'tif', filter_suffix='jpg', max_size=1, min_size=0.5)
        for img_path in img_folder.glob('*.tif'):
            self.assertTrue(img_path.exists())

        # Test converting with no size constraints
        convert(img_folder, 'pdf', filter_suffix='tif')
        for img_path in img_folder.glob('*.pdf'):
            self.assertTrue(img_path.exists())

    def test_load_image(self):
        # Test loading a valid image
        img_path = base_path / 'test_data/test_image.jpg'
        image, filename = load_image(img_path)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(filename, 'test_image')

        # Test loading an invalid image
        img_path = base_path / 'test_data/invalid_image.jpg'
        image, filename = load_image(img_path)
        self.assertIsNone(image)
        self.assertIsNone(filename)

    def test_load_images(self):
        # Test loading images from a folder
        img_folder = base_path / 'test_data'
        images = load_images(img_folder)
        self.assertEqual(len(images), 3)
        self.assertIsInstance(images[0][0], Image.Image)

        # Test loading images with a specified suffix
        images = load_images(img_folder, 'jpg')
        self.assertEqual(len(images), 1)
        self.assertIsInstance(images[0][0], Image.Image)

        # Test loading images with an invalid suffix
        images = load_images(img_folder, 'invalid')
        self.assertEqual(len(images), 0)

    def test_save(self):
        img_path = base_path / 'test_data/test_image.jpg'
        image, filename = load_image(img_path)

        # Test saving with optimization
        save(image, base_path / f'test_data/{filename}_optimized.jpg', max_size=1, min_size=0.5)
        self.assertTrue((base_path / f'test_data/{filename}_optimized.jpg').exists())

        # Test saving without optimization
        save(image, base_path / f'test_data/{filename}_unoptimized.jpg', max_size=1, min_size=0.5, min_quality=100)
        self.assertTrue((base_path / f'test_data/{filename}_unoptimized.jpg').exists())

        # Test saving with size constraints
        save(image, base_path / f'test_data/{filename}_constrained.jpg', max_size=0.5, min_size=0.25)
        self.assertTrue((base_path / f'./test_data/{filename}_constrained.jpg').exists())

        # Test saving with no size constraints
        save(image, Path(f'./test_data/{filename}_unconstrained.jpg'))
        self.assertTrue(Path(f'./test_data/{filename}_unconstrained.jpg').exists())

if __name__ == '__main__':
    generate_test_data()
    unittest.main()
