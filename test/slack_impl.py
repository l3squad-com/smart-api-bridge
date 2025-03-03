from fastapi import FastAPI
from bridge import get_db_connection
from router import ApiBridgeRouter

# Single database configuration
db_config = {
    "host": "localhost",
    "port": 3306,
    "database": "slack_db",
    "user": "root",
    "password": "1234"
}

app = FastAPI(
    title="Slack"
)
engine = get_db_connection(**db_config)

api_bridge = ApiBridgeRouter(engine,prefix="/slack")
app.include_router(api_bridge.get_router())

# Run the app
# uvicorn main:app --reload
