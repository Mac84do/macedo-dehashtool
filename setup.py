from setuptools import setup, find_packages

setup(
    name="macedo-dehashtool",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.32.0',
        'python-dotenv>=1.1.0',
    ],
    extras_require={
        'v2': [
            'numpy>=2.0.0',
            'pandas>=2.0.0',
            'rich>=13.0.0',
            'reportlab>=4.0.0',
            'typer>=0.16.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'dehashtool-v1=main:main',
            'dehashtool-v2=main_v2:main'
        ]
    },
    author="Your Name",
    description="Macedo Dehash Tool",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/macedo-dehashtool",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
