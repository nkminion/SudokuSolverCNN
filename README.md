Sudoku Solver:


A Python script that automatically detects and solves a Sudoku puzzle from an image.



Features:

Image Preprocessing: Automatically processes an input image to isolate the Sudoku grid and digits.

Grid Detection: Finds the puzzle's borders and extracts it from the image.

Digit Recognition: Uses a custom-trained CNN to identify the digits in each cell.

Puzzle Solver: Implements a backtracking algorithm to solve the detected puzzle.



Current Limitations:

Straight Images Only: The current version of the grid detection works best on images that are straight and un-rotated. Support for perspective warping is a potential future improvement.

Hardcoded Values: Kernel values and input image path is hardcoded and may need adjustment for different images.

Maintenance Status: This is a personal project and is not actively maintained. Updates and bug fixes may be infrequent.



Requirements:

Pillow (If you plan on creating your own dataset)

PyTorch (The Tensorflow version works but is not as good as the PyTorch version)

OpenCV

Numpy



License:

This project is licensed under the MIT License. See the LICENSE file for more details.
