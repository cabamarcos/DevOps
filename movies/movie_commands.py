"""Commands shared by the HTTP API and command line utilities."""

from pydantic import BaseModel

from movies.movie import Movie, MovieDetails


class CreateMovieCommand(MovieDetails):
    def execute(self):
        return self.execute_with_status()[0]

    def execute_with_status(self):
        return Movie.get_or_create(self)


class ListMovies(BaseModel):
    def execute(self):
        return Movie.list()


class GetMovieById(BaseModel):
    id: str

    def execute(self):
        return Movie.get_by_id(self.id)
