[![Actions Status](https://github.com/ludgerradke/ImgC/actions/workflows/test.yml/badge.svg)](https://github.com/ludgerradke/ImgC/actions/workflows/test.yml)

# ImgC - Image Optimizer

ImgC is a tool for optimizing images in terms of format and size. It can handle single images or a folder of images and supports the following output formats: **'png'**, **'jpg'**, **'tif'**, **'pdf'**, **'mp4'**, **'gif'**, and **'ico'**.

## Installation

To use ImgC, you will need to install the required dependencies listed in the **'requirements.txt'** file:

```basch
pip install -r requirements.txt
```

## Usage

To use ImgC, you can run the img.py function with command line arguments or use the graphical user interface (GUI).

### Command Line Interface (CLI)
To use ImgC, run the img.py function with the following arguments:

```basch
python imgc.py -f /path/to/image -s output_suffix [--filter_suffix input_suffix] [--max max_size] [--min min_size] [--fps frame_rate] [--size icon_size]
```

- **-f /path/to/image**: The path to the image file or folder of images to be optimized.
- **-s output_suffix**: The desired output format for the image(s).
- **--filter_suffix input_suffix**: (Optional) The suffix of the input image(s). If not specified, all image types will be processed.
- **--max max_size**: (Optional) The maximum size of the output image(s) in megabytes. If not specified, the size will not be constrained.
- **--min min_size**: (Optional) The minimum size of the output image(s) in megabytes. If not specified, the size will not be constrained.
- **--fps frame_rate**: (Optional) The desired frame rate for output .mp4 or .gif files. If not specified, the default frame rate is 30 fps.
- **--size icon_size**: (Optional) The desired dimensions (in pixels) of the output .ico file. If not specified, the default size is 64x64.

### Graphical User Interface

You can also use ImgC through a GUI by running **'ImageConverter.py'**. This offers the same functionality as the CLI in a more user-friendly format. It provides an easy to navigate interface, with options to select files, set parameters, and start the conversion process.

![](/assets/img.png)

For convenience, we have provided a standalone executable and an installer. These are located in the **'dist/'** and **'Output/'** directories respectively.

- The standalone executable located at **'dist/ImageConverter.exe'** is an all-in-one file, which means it can be run directly without any installation. Just double click on the **'.exe'** file and the GUI will open, ready for you to use.

- The installer located at **'Output/ImgC_setup.exe'** can be used to install the ImgC application on your system. Just run the **'.exe'** file, follow the on-screen prompts to install the application, and then you can access the ImgC GUI through the start menu or a shortcut on your desktop.

These options provide flexibility depending on whether you want to install the software or simply run it as a standalone application.



## Example

To convert all **'jpg'** images in the **'/path/to/images'** folder to **'png'** format with a maximum size of 2 MB and a minimum size of 1 MB, use the following command:

```basch
python imgc.py -f /path/to/images -s png --filter_suffix jpg --max 2 --min 1
```

# Testing the imgc script

To test the functionality of the **imgc** script, you can use the unit tests provided in the **test_imgc.py** file. These tests will verify that the script is able to correctly convert images and apply size constraints.

To run the tests, make sure you have the **unittest** module installed, and then run the following command:

```basch
python -m unittest test_imgc
```

# Contributing

We welcome contributions to the imgc project! If you have ideas for how to improve the script or have found a bug, please don't hesitate to open an issue or submit a pull request.

To contribute to the project, follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and commit them to your branch.
4. Push your branch to your fork on GitHub.
5. Create a pull request to the imgc repository.

We appreciate any and all contributions, no matter how big or small. Thank you for considering contributing to the imgc project!

Note: Please run the GitHocks before you create a Pull Request.

### Git hocks
Install "pre-commit"
```bash
pip install pre-commit
```

then run:
```bash
pre-commit install
```

# License
ImgC is licensed under the GNU GENERAL PUBLIC LICENSE Version 3. See the [LICENSE](./LICENSE) file for more information.

# Support

If you really like this repository and find it useful, please consider (★) starring it, so that it can reach a broader audience of like-minded people.

