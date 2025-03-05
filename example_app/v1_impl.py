from fastapi import FastAPI
from api_bridge.core import APIBridge

db_config = {
    "host": "localhost",
    "port": 3306,
    "database": "ecospace",
    "user": "root",
    "password": "",
}

app = FastAPI()
api_bridge = APIBridge(db_config, base_endpoint="/custom_api")
app.include_router(api_bridge.router)
