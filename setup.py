import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ezy-api",
    version="0.1.0",
    author="3xhaust, nck90",
    author_email="s2424@e-mirim.hs.kr, s2460@e-mirim.hs.kr",
    description="API 생성 및 프로젝트 관리를 위한 프레임워크",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3x-haust/Python_Ezy_API",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "inflect>=5.3.0",
        "pytest>=6.2.5",
        "flake8>=3.9.0",
        "flask>=2.0.0"
    ],
    keywords=['3xhaust', 'nck90', 'python api', 'ezy api', 'backend', 'cli'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'ezy = ezycli:main'
        ],
    },
    python_requires='>=3.6',
)   