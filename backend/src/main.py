"""Start the backend server."""

import argparse

import uvicorn
from dotenv import load_dotenv

from app import create_app
from core.settings import load_settings

load_dotenv()
settings = load_settings()
app = create_app(settings)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the backend server.")
    parser.add_argument("--dev", action="store_true", help="Reload when the code changes.")
    args = parser.parse_args()

    if args.dev:
        # Uvicorn reloads only an app it can import again by name.
        uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
    else:
        uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
