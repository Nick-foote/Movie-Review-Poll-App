from contextlib import contextmanager
import datetime

# -- PostGreSQL Queries --

# create all required tables
CREATE_MOVIES_TABLE = """CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title TEXT,
    release_timestamp REAL,
    trailer_url TEXT
);"""

CREATE_USERS_TABLE = """CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY
);"""

CREATE_REVIEWS_TABLE = """CREATE TABLE IF NOT EXISTS reviews (
    user_username TEXT,
    movie_id INTEGER,
    review TEXT,
    FOREIGN KEY (user_username) REFERENCES users (username),
    FOREIGN KEY (movie_id) REFERENCES movies (id)
);"""

# will make searching for films quicker from from PostGreSQL
CREATE_RELEASE_INDEX = "CREATE INDEX IF NOT EXISTS idx_movies_release ON movies (release_timestamp)"

INSERT_USER = "INSERT INTO users (username) VALUES (%s);"
INSERT_MOVIES = "INSERT INTO movies (title, release_timestamp, trailer_url) VALUES (%s, %s, %s);"
INSERT_REVIEWED_MOVIE = "INSERT INTO reviews (user_username, movie_id, review) VALUES (%s, %s, %s);"

SELECT_MOVIES = "SELECT * FROM movies;"
SELECT_UPCOMING_MOVIES = "SELECT * FROM movies WHERE release_timestamp > %s;"

SELECT_REVIEWED_MOVIES = """SELECT movies.title, movies.release_timestamp, reviews.review 
    FROM movies JOIN reviews ON movies.id = reviews.movie_id
    JOIN users ON users.username = reviews.user_username
    WHERE users.username = %s;
"""

SELECT_MOVIE_REVIEWS = """SELECT movies.title, users.username, reviews.review 
    FROM movies JOIN reviews ON movies.id = reviews.movie_id
    JOIN users on users.username = reviews.user_username
    WHERE movies.id = %s;
"""

SELECT_MOVIE_TRAILER_URL = "SELECT trailer_url FROM movies WHERE title = %s"
SEARCH_MOVIE = "SELECT * FROM movies WHERE title LIKE %s;"
GET_MOVIE_TITLE = "SELECT title FROM movies WHERE id = %s;"

@contextmanager
def get_cursor(connection):
    with connection:
        with connection.cursor() as cursor:
            yield cursor


def create_tables(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(CREATE_MOVIES_TABLE)
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(CREATE_REVIEWS_TABLE)
        cursor.execute(CREATE_RELEASE_INDEX)


def add_movie(connection, title: str, release_timestamp: str, trailer_url: str):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_MOVIES, (title, release_timestamp, trailer_url))


def add_user(connection, username: str):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_USER, (username, ))


def get_movies(connection, upcoming=False):
    with get_cursor(connection) as cursor:
        if upcoming:
            today_timestamp = datetime.datetime.today().timestamp()
            cursor.execute(SELECT_UPCOMING_MOVIES, (today_timestamp, ))
        else:
            cursor.execute(SELECT_MOVIES)
        return cursor.fetchall()


def review_movie(connection, username: str, movie_id: str, review: str):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_REVIEWED_MOVIE, (username, movie_id, review))


def get_reviewed_movies(connection, username: str):
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_REVIEWED_MOVIES, (username, ))
        return cursor.fetchall()


def get_movie_reviews(connection, movie_id: str):
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_MOVIE_REVIEWS, (movie_id, ))
        return cursor.fetchall()


def get_trailer_url(connection, title: str):
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_MOVIE_TRAILER_URL, (title, ))
        return cursor.fetchone()


def search_movie(connection, search_input: str):
    with get_cursor(connection) as cursor:
        cursor.execute(SEARCH_MOVIE, (f"%{search_input}%", ))
        return cursor.fetchall()
