import json
import pathlib

import pytest
from jsonschema import validate, RefResolver

from web_app import app
from movies.movie import Movie


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def validate_payload(payload, schema_name):
    """
    Validate payload with selected schema
    """
    schemas_dir = str(
        f"{pathlib.Path(__file__).parent.absolute()}/schemas"
    )
    schema = json.loads(pathlib.Path(f"{schemas_dir}/{schema_name}").read_text())
    validate(
        payload,
        schema,
        resolver=RefResolver(
            "file://" + str(pathlib.Path(f"{schemas_dir}/{schema_name}").absolute()),
            schema  # it's used to resolve the file inside schemas correctly
        )
    )


def test_create_movie(client):
    data = {
        "title": "Avatar",
        "duration": 178,
        "category": "Action"
    }
    response = client.post(
        "/create-movie/",
        data=json.dumps(
            data
        ),
        content_type="application/json",
    )

    validate_payload(response.json, "Movie.json")


def test_get_movie(client):

    movie = Movie(
        title = "Avatar",
        duration = 178,
        category = "Action"
    ).save()

    response = client.get(
        f"/movie/{movie.id}/",
        content_type="application/json",
    )

    validate_payload(response.json, "Movie.json")


def test_list_movies(client):

    Movie(
        title = "Avatar",
        duration = 178,
        category = "Action"
    ).save()
    response = client.get(
        "/movie-list/",
        content_type="application/json",
    )

    validate_payload(response.json, "MovieList.json")