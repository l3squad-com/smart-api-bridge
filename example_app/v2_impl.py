from fastapi import FastAPI
from api_bridge.core import APIBridge

# Multiple MySQL database configurations
db_configs = {
    "db1": {
        "host": "localhost",
        "port": 3306,
        "database": "database1",
        "user": "user1",
        "password": "pass1",
    },
    "db2": {
        "host": "localhost",
        "port": 3306,
        "database": "database2",
        "user": "user2",
        "password": "pass2",
    },
}

app = FastAPI()
api_bridge = APIBridge(db_configs)
app.include_router(api_bridge.router)

# Run the app
# uvicorn main:app --reload
