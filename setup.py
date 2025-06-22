from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="durc_is_crud",
    version="0.1.0",
    author="Fred Trotter",
    author_email="fred@example.com",  # Replace with actual email
    description="A package for Database to CRUD operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ftrotter/durc_is_crud",  # Replace with actual URL
    packages=find_packages(include=['durc_is_crud', 'durc_is_crud.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
    ],
    python_requires=">=3.6",
    install_requires=[
        "django>=3.0.0",
        "pytest>=6.0.0",
        "pytest-django>=4.0.0",
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "flake8",
            "coverage",
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/ftrotter/durc_is_crud/issues",
        "Source": "https://github.com/ftrotter/durc_is_crud",
        "Documentation": "https://github.com/ftrotter/durc_is_crud/tree/main/docs",
    },
)
