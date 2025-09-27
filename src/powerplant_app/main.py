import uvicorn
import os
from pathlib import Path
from .app import app

HERE = Path(__file__).parent


def get_launch_options() -> dict:
    if os.environ.get("DEBUG"):
        print("Running with reload enabled")
        return {
            "app": "powerplant_app.app:app",
            "reload": True,
            "reload_dirs": [HERE.parent],
        }
    return {"app": app}


def main():
    uvicorn.run(
        host="0.0.0.0",
        port=8888,
        **get_launch_options(),
    )


if __name__ == "__main__":
    main()
