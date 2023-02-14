import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="galvanalyser",
    version="0.0.1",
    author="Martin Robinson",
    author_email="martin.robinson@cs.ox.ac.uk",
    description="galvanalyser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'sqlalchemy==1.4.46',
        'sqlalchemy_utils',
        'marshmallow',
        'intervals',
        'psycopg2-binary',
        'flask-login',
        'flask-cors',
        'flask-jwt-extended',
        'celery[redis]',
        'py3-validate-email',
        'galvani',
        'psutil',
        'maya',
        'xlrd==1.2.0',
        'openpyxl'
    ]
)
