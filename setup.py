import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sent_segment",
    packages = ['sent_segment'],
    version="1.0",
    author="Reverie Language Technologies",
    author_email="astha.manchanda@reverieinc.com",
    description="A sentence segmentation API",
    #long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reverieinc/rosetta_apis",
    #packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
          'markdown',
      ]
)