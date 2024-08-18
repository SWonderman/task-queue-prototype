import os

from uvicorn import run

from queueproto.wsgi import fastapp_v1

if __name__ == "__main__":
    run(fastapp_v1, host="0.0.0.0", port=8000)
