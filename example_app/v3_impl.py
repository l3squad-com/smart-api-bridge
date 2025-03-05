from fastapi import FastAPI
from api_bridge.core import APIBridge

# Configuring MySQL and PostgreSQL databases
db_configs = {
    "mysql_db": {
        "type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "mysql_db",
        "user": "mysql_user",
        "password": "mysql_pass",
    },
    "postgres_db": {
        "type": "postgres",
        "host": "localhost",
        "port": 5432,
        "database": "postgres_db",
        "user": "postgres_user",
        "password": "postgres_pass",
    },
}

app = FastAPI()
api_bridge = APIBridge(db_configs)
app.include_router(api_bridge.router)

# Run the app
# uvicorn main:app --reload
