from pydantic import BaseModel
from typing import List
from movies.movie import Movie


class CreateMovieCommand(BaseModel):
    title: str
    duration: int
    category: str

    def execute(self) -> Movie:
        movie = Movie.get_by_title(self.title)
        if movie is None:
            movie = Movie(
                title=self.title, duration=self.duration, category=self.category
            ).save()
            return movie
        else:
            return movie


class ListMovies(BaseModel):

    def execute(self) -> List[Movie]:
        movies = Movie.list()
        return movies


class GetMovieById(BaseModel):
    id: str

    def execute(self) -> Movie:
        movie = Movie.get_by_id(self.id)
        return movie
