# opencv-draw-tools
Library to help the drawing process with OpenCV. Thought to add labels to the images. Classification of images, etc.

## Installation

### Pre-requisites

You will need to install:

* opencv >= 3.6.2
* numpy >= 1.13.3

You can simply execute:
`pip install -r requirements.txt`

Finally you can install the library with:

`pip install opencv-draw-tools-fernaperg`

When you install `opencv-draw-tools`, it will automatically download `numpy` but not opencv becouse in some cases you will need another version.

## Usage

```
import opencv_draw_tools as cv2_tools

print('Name: {}\nVersion:{}\nHelp:{}'.format(cv2_tools.name,cv2_tools.version,cv2_tools.help))
cv2_tools.webcam_test()
```
