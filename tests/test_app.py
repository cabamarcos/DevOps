import json
from pathlib import Path

import pytest
from jsonschema import validate

from web_app import create_app

PAYLOAD = {"title": "Avatar", "duration": 178, "category": "Action"}
SCHEMA = json.loads((Path(__file__).parent / "schemas" / "Movie.json").read_text())


def test_full_movie_lifecycle(client):
    assert client.get("/movies").json == []
    response = client.post("/movies", json=PAYLOAD)
    assert response.status_code == 201
    validate(response.json, SCHEMA)
    movie_id = response.json["id"]
    assert client.get(response.headers["Location"]).json == response.json
    assert client.get("/movies").json == [response.json]
    update = client.put(f"/movies/{movie_id}", json={**PAYLOAD, "duration": 180})
    assert update.status_code == 200 and update.json["duration"] == 180
    assert update.json["id"] == movie_id
    deletion = client.delete(f"/movies/{movie_id}")
    assert deletion.status_code == 204 and deletion.data == b""
    assert client.get(f"/movies/{movie_id}").status_code == 404


def test_legacy_routes(client):
    created = client.post("/create-movie/", json=PAYLOAD)
    assert created.status_code == 201
    assert client.get(f"/movie/{created.json['id']}/").json == created.json
    assert client.get("/movie-list/").json == [created.json]


def test_duplicate_and_conflict(client):
    first = client.post("/movies", json=PAYLOAD)
    repeat = client.post("/movies", json=PAYLOAD)
    assert repeat.status_code == 200 and repeat.json == first.json
    conflict = client.post("/movies", json={**PAYLOAD, "duration": 100})
    assert conflict.status_code == 409
    assert client.get("/movies").json == [first.json]


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing_movie(client, method):
    kwargs = {"json": PAYLOAD} if method == "put" else {}
    response = getattr(client, method)("/movies/missing", **kwargs)
    assert response.status_code == 404 and "message" in response.json


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {**PAYLOAD, "duration": -1},
        {**PAYLOAD, "title": " "},
        {**PAYLOAD, "unexpected": 1},
    ],
)
def test_invalid_payload(client, payload):
    response = client.post("/movies", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 422
    assert client.get("/movies").json == []


def test_invalid_json_and_content_type(client):
    assert client.post("/movies", data="{", content_type="application/json").status_code == 400
    assert client.post("/movies", data="text").status_code == 415
    assert client.get("/unknown").status_code == 404
    assert client.patch("/movies").status_code == 405


def test_update_conflict(client):
    first = client.post("/movies", json=PAYLOAD).json
    second = client.post("/movies", json={**PAYLOAD, "title": "Arrival"}).json
    assert client.put(f"/movies/{second['id']}", json=PAYLOAD).status_code == 409
    assert client.get(f"/movies/{second['id']}").json == second
    assert client.get(f"/movies/{first['id']}").json == first


def test_apps_have_isolated_persistent_databases(tmp_path):
    path = str(tmp_path / "first.db")
    first = create_app({"TESTING": True, "DATABASE": path}).test_client()
    second = create_app({"TESTING": True, "DATABASE": str(tmp_path / "second.db")}).test_client()
    record = first.post("/movies", json=PAYLOAD).json
    assert second.get("/movies").json == []
    reopened = create_app({"TESTING": True, "DATABASE": path}).test_client()
    assert reopened.get("/movies").json == [record]


def test_seed_is_repeatable(app, client):
    first = app.test_cli_runner().invoke(args=["seed"])
    assert first.exit_code == 0, first.output
    count = len(client.get("/movies").json)
    assert count > 0
    second = app.test_cli_runner().invoke(args=["seed"])
    assert second.exit_code == 0 and "Películas añadidas: 0" in second.output
    assert len(client.get("/movies").json) == count


def test_health(client):
    assert client.get("/health/").json == {"status": "ok"}
