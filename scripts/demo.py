"""Exercise the running API using only Python's standard library."""

import argparse
import json
import uuid
from urllib.request import Request, urlopen


def call(base, method, path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        base + path, data=body, method=method, headers={"Content-Type": "application/json"}
    )
    with urlopen(request, timeout=10) as response:  # noqa: S310 -- local API demo
        data = response.read()
        print(f"{method} {path}: {response.status}")
        return json.loads(data) if data else None


def main():
    parser = argparse.ArgumentParser(description="Demostración de la API de películas")
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    base = parser.parse_args().url.rstrip("/")
    payload = {"title": f"Demo {uuid.uuid4()}", "duration": 120, "category": "Drama"}
    created = call(base, "POST", "/movies", payload)
    path = f"/movies/{created['id']}"
    try:
        call(base, "GET", path)
        call(base, "PUT", path, {**payload, "duration": 125})
        call(base, "GET", "/movies")
    finally:
        call(base, "DELETE", path)
    print("Demostración completada; el registro de prueba se ha eliminado.")


if __name__ == "__main__":
    main()
