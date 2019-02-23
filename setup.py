import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="opencv-draw-tools-fernaperg",
    version="0.1.1",
    author="Fernando Pérez",
    author_email="fernaperg@gmail.com",
    description="Library to help the drawing process with OpenCV. Thought to add labels to the images. Classification of images, etc.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fernaper/opencv-draw-tools",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        #'opencv-python',
        'numpy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
