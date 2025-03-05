import uvicorn


def main():
    uvicorn.run("api_bridge.routes:router", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
