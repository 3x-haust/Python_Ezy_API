import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ezyapi",
    version="0.0.1",
    author="3xhaust, nck90",
    author_email="s2424@e-mirim.hs.kr, s2460@e-mirim.hs.k",
    description="Frameworks for creating APIs without controllers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3x-haust/Python_Ezy_API",
    install_requires=[
        'fastapi',
        'pydantic',
        'uvicorn',
        'inflect',
    ],
    license_file='MIT',
    keywords=['3xhaust', 'nck90', 'python api', 'ezy api', 'backend'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
