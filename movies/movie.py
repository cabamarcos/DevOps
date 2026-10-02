"""Validated movie records and transactional SQLite persistence."""

import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

from flask import current_app, has_app_context
from pydantic import BaseModel, ConfigDict, Field


class MovieConflict(Exception):
    """A title already belongs to a different movie."""


class MovieDetails(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    duration: int = Field(gt=0, strict=True)
    category: str = Field(min_length=1, max_length=100)


@contextmanager
def connection(database_name=None):
    """Commit or roll back and always close, including failed reads."""
    if database_name is None:
        database_name = (
            current_app.config["DATABASE"]
            if has_app_context()
            else os.getenv("DATABASE_NAME", "movies.db")
        )
    con = sqlite3.connect(database_name, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()


class Movie(MovieDetails):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def get_by_id(cls, movie_id: str):
        with connection() as con:
            row = con.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
        return cls(**row) if row else None

    @classmethod
    def get_by_title(cls, title: str):
        with connection() as con:
            row = con.execute(
                "SELECT * FROM movies WHERE title = ? COLLATE NOCASE", (title.strip(),)
            ).fetchone()
        return cls(**row) if row else None

    @classmethod
    def list(cls):
        with connection() as con:
            rows = con.execute("SELECT * FROM movies ORDER BY title COLLATE NOCASE, id")
            return [cls(**row) for row in rows]

    def save(self):
        try:
            with connection() as con:
                con.execute(
                    "INSERT INTO movies (id, title, duration, category) VALUES (?, ?, ?, ?)",
                    (self.id, self.title, self.duration, self.category),
                )
        except sqlite3.IntegrityError as exc:
            raise MovieConflict("Ya existe una película con ese título o identificador.") from exc
        return self

    @classmethod
    def get_or_create(cls, details: MovieDetails):
        """Serialize lookup and insert so concurrent requests cannot duplicate titles."""
        with connection() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM movies WHERE title = ? COLLATE NOCASE", (details.title,)
            ).fetchone()
            if row:
                movie = cls(**row)
                if movie.duration != details.duration or movie.category != details.category:
                    raise MovieConflict("El título ya existe con otros datos.")
                return movie, False
            movie = cls(**details.model_dump())
            con.execute(
                "INSERT INTO movies (id, title, duration, category) VALUES (?, ?, ?, ?)",
                (movie.id, movie.title, movie.duration, movie.category),
            )
            return movie, True

    @classmethod
    def update(cls, movie_id: str, details: MovieDetails):
        try:
            with connection() as con:
                result = con.execute(
                    "UPDATE movies SET title = ?, duration = ?, category = ? WHERE id = ?",
                    (details.title, details.duration, details.category, movie_id),
                )
        except sqlite3.IntegrityError as exc:
            raise MovieConflict("Ya existe otra película con ese título.") from exc
        return cls(id=movie_id, **details.model_dump()) if result.rowcount else None

    @classmethod
    def delete(cls, movie_id: str):
        with connection() as con:
            return con.execute("DELETE FROM movies WHERE id = ?", (movie_id,)).rowcount > 0

    @classmethod
    def create_table(cls, database_name=None):
        if database_name and database_name != ":memory:":
            Path(database_name).parent.mkdir(parents=True, exist_ok=True)
        with connection(database_name) as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS movies ("
                "id TEXT PRIMARY KEY, title TEXT NOT NULL COLLATE NOCASE UNIQUE, "
                "duration INTEGER NOT NULL CHECK (duration > 0), category TEXT NOT NULL)"
            )

    @classmethod
    def delete_rows(cls, database_name=None):
        with connection(database_name) as con:
            con.execute("DELETE FROM movies")
