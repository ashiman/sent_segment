import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sent_segment",
    packages=['sent_segment'],
    version="2.0.2",
    author="Reverie Language Technologies",
    author_email="astha.manchanda@reverieinc.com",
    description="A sentence segmentation API",
    #long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashiman/sent_segment",
    dowload_link = 'https://github.com/ashiman/sent_segment/archive/1.0.tar.gz',
    #packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
          'spacy==2.0.0',
          'numpy',
          'unidecode',

      ]
)