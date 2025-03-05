# smart-api-bridge

A flexible and dynamic CRUD (Create, Read, Update, Delete) operations library for FastAPI applications with MySQL database support.

## Features

- Dynamic CRUD operations for any MySQL table
- Simple integration with FastAPI
- Automatic pagination
- Supports both hard delete and soft delete operations
- Partial updates via the PATCH method
- Configurable database connection
- Secure authentication and authorization support

## Installation

```bash
pip install smart-api-bridge
```

## Quick Start

```python
from fastapi import FastAPI
from api_bridge import APIBridge

app = FastAPI()

# Configure database connection
db_config = {
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "username",
    "password": "password@123",
}


# Initialize APIBridge
api_bridge = APIBridge(db_config)

# Create FastAPI app
app = FastAPI()
app.include_router(api_bridge.router)

# Run with uvicorn
# uvicorn main:app --reload
```

## Available Endpoints

| Method  | Endpoint                                  | Description                           |
|---------|-------------------------------------------|---------------------------------------|
| GET     | `/api/test`                              | Test database connection             |
| GET     | `/api/{table_name}`                      | Fetch all records (supports pagination)  |
| POST    | `/api/{table_name}`                      | Insert a new record                  |
| PUT     | `/api/{table_name}/{record_id}`          | Update an existing record            |
| PATCH   | `/api/{table_name}/{record_id}`          | Partially update a record            |
| DELETE  | `/api/{table_name}/{record_id}`          | Soft delete a record                 |
| DELETE  | `/api/{table_name}/{record_id}/hard`     | Permanently delete a record          |

## Example Applications

### 1. E-commerce Product Management System

Manage products, categories, inventory, and orders using dynamic CRUD operations:

```python
import os
from fastapi import FastAPI
from api_bridge import APIBridge

app = FastAPI(title="E-commerce API")

# Load database config
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "ecommerce"),
    "user": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASS", "password"),
}

# Initialize APIBridge
api_bridge = APIBridge(db_config)

app.include_router(api_bridge.router)

@app.get("/")
def read_root():
    return {"message": "E-commerce API ready"}
```

### 2. Content Management System (CMS)

Manage blog posts, pages, users, and media files:

```python
from fastapi import FastAPI
from api_bridge import 
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="CMS API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load database config
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "cms"),
    "user": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASS", "password"),
}

# Initialize APIBridge
api_bridge = APIBridge(db_config)

app.include_router(api_bridge.router)

@app.get("/")
def read_root():
    return {"message": "CMS API ready"}
```

## Workflow to Publish as a PyPI Package

1. **Prepare Your Package Structure**:
   ```
   smart-api-bridge/
   ├── smart_api_bridge/
   │   ├── __init__.py
   │   ├── db.py
   │   ├── router.py
   ├── setup.py
   ├── README.md
   ├── LICENSE
   └── requirements.txt
   ```

2. **Test Your Package Locally**:
   ```bash
   pip install -e .
   ```

3. **Build Your Package**:
   ```bash
   pip install build
   python -m build
   ```

4. **Upload to PyPI Test**:
   ```bash
   pip install twine
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```

5. **Test Your Package from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ smart-api-bridge
   ```

6. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
