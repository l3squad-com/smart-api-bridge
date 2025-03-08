from setuptools import setup, find_packages

setup(
    name="smart_api_bridge",
    version="0.1.2",
    description="A FastAPI-based CRUD API generator for MySQL databases",
    author="Venkat.R",
    author_email="ai.venkat.r@gmail.com",
    packages=find_packages(),
    install_requires=["fastapi", "sqlalchemy", "pymysql", "uvicorn"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
