import pytest

from movies.movie import Movie
from web_app import create_app


@pytest.fixture(autouse=True)
def database(tmp_path, monkeypatch):
    path = str(tmp_path / "movies.db")
    monkeypatch.setenv("DATABASE_NAME", path)
    Movie.create_table(path)
    return path


@pytest.fixture
def app(database):
    return create_app({"TESTING": True, "DATABASE": database})


@pytest.fixture
def client(app):
    return app.test_client()
