"""Movie catalog API. Run with flask --app web_app run."""

import csv
import os
from pathlib import Path

import click
from flask import Flask, jsonify, request, url_for
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException, NotFound, UnprocessableEntity

from movies.movie import Movie, MovieConflict, MovieDetails
from movies.movie_commands import CreateMovieCommand


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.getenv("DATABASE_NAME", str(Path(app.instance_path) / "movies.db"))
    )
    if config:
        app.config.update(config)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        Movie.create_table()

    def movie_details(model=MovieDetails):
        payload = request.get_json()
        if not isinstance(payload, dict):
            raise UnprocessableEntity("El cuerpo JSON debe ser un objeto.")
        return model(**payload)

    @app.errorhandler(ValidationError)
    def invalid_movie(error):
        return jsonify(
            error="validation_error",
            message="Revisa los campos de la película.",
            details=error.errors(include_url=False, include_context=False, include_input=False),
        ), 422

    @app.errorhandler(MovieConflict)
    def conflicting_movie(error):
        return jsonify(error="conflict", message=str(error)), 409

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.name, message=error.description), error.code

    @app.get("/health/")
    def health():
        return jsonify(status="ok")

    @app.post("/movies")
    @app.post("/create-movie/")
    def create_movie():
        movie, created = movie_details(CreateMovieCommand).execute_with_status()
        response = jsonify(movie.model_dump())
        response.status_code = 201 if created else 200
        response.headers["Location"] = url_for("get_movie", movie_id=movie.id)
        return response

    @app.get("/movies/<movie_id>")
    @app.get("/movie/<movie_id>/")
    def get_movie(movie_id):
        movie = Movie.get_by_id(movie_id)
        if movie is None:
            raise NotFound("No existe esa película.")
        return jsonify(movie.model_dump())

    @app.get("/movies")
    @app.get("/movie-list/")
    def list_movies():
        return jsonify([movie.model_dump() for movie in Movie.list()])

    @app.put("/movies/<movie_id>")
    @app.put("/movie/<movie_id>/")
    def update_movie(movie_id):
        movie = Movie.update(movie_id, movie_details())
        if movie is None:
            raise NotFound("No existe esa película.")
        return jsonify(movie.model_dump())

    @app.delete("/movies/<movie_id>")
    @app.delete("/movie/<movie_id>/")
    def delete_movie(movie_id):
        if not Movie.delete(movie_id):
            raise NotFound("No existe esa película.")
        return "", 204

    @app.cli.command("seed")
    @click.option(
        "--csv-file",
        type=click.Path(exists=True, path_type=Path),
        default=Path(__file__).parent / "movies" / "movies.csv",
    )
    def seed(csv_file):
        """Import the sample CSV; repeated imports do not duplicate movies."""
        count = 0
        with csv_file.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                details = dict(
                    title=row["MOVIE_NAME"], duration=int(row["DURATION"]), category=row["CATEGORY"]
                )
                _, created = CreateMovieCommand(**details).execute_with_status()
                count += created
        click.echo(f"Películas añadidas: {count}")

    return app


app = create_app()

if __name__ == "__main__":
    app.run()
