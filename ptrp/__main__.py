"""Run the production PTRP instance: python -m ptrp"""

from __future__ import annotations

import os

import uvicorn

from ptrp.app import create_app


def main():
    host = os.environ.get("PTRP_HOST", "0.0.0.0")
    port = int(os.environ.get("PTRP_PORT", "8000"))
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
