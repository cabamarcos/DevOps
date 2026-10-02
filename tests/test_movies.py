import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError

from movies.movie import Movie, MovieConflict, MovieDetails, connection
from movies.movie_commands import CreateMovieCommand, GetMovieById, ListMovies


def details(title="Avatar", duration=178, category="Action"):
    return dict(title=title, duration=duration, category=category)


def test_create_and_find_movie():
    movie = CreateMovieCommand(**details()).execute()
    assert GetMovieById(id=movie.id).execute() == movie
    assert Movie.get_by_title(" AVATAR ") == movie
    assert ListMovies().execute() == [movie]


def test_repeated_creation_is_idempotent():
    first, created = CreateMovieCommand(**details()).execute_with_status()
    second, repeated = CreateMovieCommand(**details(title="avatar")).execute_with_status()
    assert created and not repeated
    assert first == second
    assert len(Movie.list()) == 1


def test_conflicting_creation_does_not_overwrite():
    first = CreateMovieCommand(**details()).execute()
    with pytest.raises(MovieConflict):
        CreateMovieCommand(**details(duration=200)).execute()
    assert Movie.get_by_id(first.id) == first


def test_concurrent_creates_share_one_movie():
    def create(_):
        return CreateMovieCommand(**details()).execute().id

    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(create, range(12)))
    assert len(set(ids)) == 1
    assert len(Movie.list()) == 1


def test_missing_reads_and_deletion():
    assert Movie.get_by_id("missing") is None
    assert Movie.get_by_title("missing") is None
    assert not Movie.delete("missing")
    assert Movie.update("missing", MovieDetails(**details())) is None


def test_update_and_delete():
    movie = Movie(**details()).save()
    updated = Movie.update(movie.id, MovieDetails(**details(title="Arrival")))
    assert updated.id == movie.id
    assert Movie.get_by_id(movie.id).title == "Arrival"
    assert Movie.get_by_title("Avatar") is None
    assert Movie.delete(movie.id)
    assert Movie.list() == []


def test_unique_title_update_rolls_back():
    first = Movie(**details()).save()
    second = Movie(**details(title="Arrival")).save()
    with pytest.raises(MovieConflict):
        Movie.update(second.id, MovieDetails(**details()))
    assert Movie.get_by_id(second.id) == second
    assert Movie.get_by_id(first.id) == first


def test_sql_is_parameterized():
    title = "'); DROP TABLE movies; --"
    movie = Movie(**details(title=title)).save()
    assert Movie.get_by_title(title) == movie
    assert Movie.get_by_id("' OR 1=1 --") is None
    assert len(Movie.list()) == 1


def test_database_enforces_constraints():
    with pytest.raises(sqlite3.IntegrityError), connection() as con:
        con.execute("INSERT INTO movies VALUES ('id', 'invalid', 0, 'Action')")
    movie = Movie(**details()).save()
    with pytest.raises(MovieConflict):
        Movie(**details(title="avatar")).save()
    assert Movie.list() == [movie]


@pytest.mark.parametrize("value", [0, -5, True, "120", 2.5])
def test_invalid_duration(value):
    with pytest.raises(ValidationError):
        MovieDetails(**details(duration=value))


@pytest.mark.parametrize("field", ["title", "category"])
def test_blank_text(field):
    payload = details()
    payload[field] = "   "
    with pytest.raises(ValidationError):
        MovieDetails(**payload)
