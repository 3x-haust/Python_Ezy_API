import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ezyapi",
    version="0.0.6",
    author="3xhaust, nck90",
    author_email="s2424@e-mirim.hs.kr, s2460@e-mirim.hs.kr",
    description="API 생성 및 프로젝트 관리를 위한 프레임워크",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3x-haust/Python_Ezy_API",
    keywords=['3xhaust', 'nck90', 'python api', 'ezy api', 'backend', 'cli'],
    license_file='MIT',
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
