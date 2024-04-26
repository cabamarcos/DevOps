import pytest

from movies.movie import Movie
from movies.movie_commands import CreateMovieCommand, ListMovies

@pytest.fixture(autouse=True)
def database():
    Movie.create_table()
    yield
    Movie.delete_rows()
    
def test_create_movie():
    """
        INPUT:
        OUTPUT: 
    """

    cmd = CreateMovieCommand(
        title = "Avatar",
        duration = 178,
        category = "Action"
    )

    movie = cmd.execute()

    db_movie = Movie.get_by_id(movie.id)

    assert db_movie != None
    assert db_movie.id == movie.id
    assert db_movie.title == movie.title
    assert db_movie.duration == movie.duration
    assert db_movie.category == movie.category


def test_create_movie_already_exists():
    """
        INPUT:
        OUTPUT: 
    """
    Movie(
        title = "Avatar",
        duration = 178,
        category = "Action"
    ).save()

    cmd = CreateMovieCommand(
        title = "Avatar",
        duration = 178,
        category = "Action"
    )

    movie = cmd.execute()
    #Assert ¿si ya existe?

def test_list_movies():
    """
    INPUT
    OUTPUT:
    """
    Movie(
        title = "Avatar",
        duration = 178,
        category = "Action"
    ).save()
    
    Movie(
        title = "Spider-Man 3",
        duration = 156,
        category = "Action"
    ).save()

    query = ListMovies()

    assert len(query.execute()) == 2
