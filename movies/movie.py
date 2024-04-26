import os
import sqlite3
import uuid
from typing import List

from pydantic import BaseModel, Field


class Movie(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    duration: int
    category: str

    @classmethod
    def get_by_id(cls, movie_id: str):
        movie = None
        con = sqlite3.connect(os.getenv("DATABASE_NAME", "movies.db"))
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM movies WHERE id=?", (movie_id,))

        record = cur.fetchone()

        if record is not None:
            movie = cls(**record)
            con.close()

        return movie

    @classmethod
    def get_by_title(cls, title: str):
        movie = None
        con = sqlite3.connect(os.getenv("DATABASE_NAME", "movies.db"))
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM movies WHERE title = ?", (title,))

        record = cur.fetchone()

        if record is not None:
            movie = cls(**record)
            con.close()

        return movie

    @classmethod
    def list(cls) -> List["Movie"]:
        con = sqlite3.connect(os.getenv("DATABASE_NAME", "movies.db"))
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM movies")

        records = cur.fetchall()
        movies = [cls(**record) for record in records]
        con.close()

        return movies

    def save(self) -> "Movie":
        with sqlite3.connect(os.getenv("DATABASE_NAME", "movies.db")) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO movies (id, title, duration, category) VALUES(?, ?, ?, ?)",
                (self.id, self.title, self.duration, self.category),
            )
            con.commit()

        return self

    @classmethod
    def create_table(cls, database_name="movies.db"):
        conn = sqlite3.connect(database_name)

        conn.execute(
            "CREATE TABLE IF NOT EXISTS movies (id TEXT, title TEXT, duration INT, category TEXT)"
        )
        conn.close()

    @classmethod
    def delete_rows(cls, database_name="movies.db"):
        conn = sqlite3.connect(database_name)

        conn.execute("DELETE FROM movies")
        conn.commit()
        conn.close()
