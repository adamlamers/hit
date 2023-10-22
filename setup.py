from setuptools import setup

setup(
    name="hit",
    version="0.1",
    description="HTTP testing on the filesystem",
    author="Adam Lamers",
    author_email="adamlamers@gmail.com",
    url="",
    install_requires=[
        "click==8.1.7",
        "requests"
    ],
    extras_require={
        "test": [
            "responses"
        ],
    },
    entry_points={
        "console_scripts": [
            "hit = hit.cli:cli"
        ]
    },
    package_dir={"": "lib"},
    packages=["hit"],
    include_package_data=True,
    zip_safe=False,
)
