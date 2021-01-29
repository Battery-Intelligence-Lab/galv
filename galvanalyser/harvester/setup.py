import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="harvester",
    version="0.0.1",
    author="Martin Robinson",
    author_email="martin.robinson@cs.ox.ac.uk",
    description="Harvester CLI application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'psutil',
        'psycopg2-binary',
        'maya',
        'xlrd',
    ]
)
