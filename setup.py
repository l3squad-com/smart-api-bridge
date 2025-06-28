from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name="smart_api_bridge",
    version="0.1.3",
    description="A FastAPI-based CRUD API generator for MySQL databases",
    author="Venkat.R",
    author_email="ai.venkat.r@gmail.com",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "pymysql",
        "uvicorn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    long_description=long_description,
    long_description_content_type='text/markdown',
)
