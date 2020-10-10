from contextlib import contextmanager
from typing import List, Tuple


# -- Function Hints --

Poll = Tuple[int, str, str]     # polls.id, polls.title, polls.owner

Option = Tuple[int, str, int]       # options.id, options.option_text, options.poll_id

Vote = Tuple[str, int]      # votes.username, votes.option_id


# -- PostGreSQL Queries --

CREATE_POLLS_TABLE = """CREATE TABLE IF NOT EXISTS polls 
    (id SERIAL PRIMARY KEY,
    title TEXT,
    owner TEXT);
"""

CREATE_POLL_OPTIONS_TABLE = """CREATE TABLE IF NOT EXISTS options 
    (id SERIAL PRIMARY KEY,
    option_text TEXT,
    poll_id INTEGER,
    FOREIGN KEY (poll_id) REFERENCES polls (id)
);"""

CREATE_VOTES_TABLE = """CREATE TABLE IF NOT EXISTS votes  
    (username TEXT,
    option_id INTEGER,
    vote_timestamp INTEGER,
    FOREIGN KEY (option_id) REFERENCES options (id)
);"""

INSERT_VOTE = "INSERT INTO votes (username, option_id, vote_timestamp) VALUES (%s, %s, %s);"
INSERT_POLL_RETURN_ID = "INSERT INTO polls (title, owner) VALUES (%s, %s) RETURNING id;"
INSERT_OPTION_RETURN_ID = "INSERT INTO options (option_text, poll_id) VALUES (%s, %s) RETURNING id;"

SELECT_ALL_POLLS = "SELECT * FROM polls"
SELECT_POLL = "SELECT * FROM polls WHERE id = %s;"
SELECT_POLL_OPTIONS = "SELECT * FROM options WHERE poll_id = %s;"
SELECT_OPTION = "SELECT * FROM options WHERE id = %s;"
SELECT_LATEST_POLL = "SELECT * FROM polls WHERE id = (SELECT id FROM polls ORDER BY id DESC LIMIT 1);"
SELECT_VOTES_FOR_OPTION = "SELECT * FROM votes WHERE option_id = %s;"
SELECT_POLLS_VOTE_COUNT = """
    SELECT polls.title, COUNT(votes.option_id) FROM polls
    JOIN options ON options.poll_id = polls.id
    JOIN votes ON options.id = votes.option_id
    GROUP BY polls.title
;"""
SELECT_POLL_OPTION_VOTES = """
    SELECT option_text, COUNT(votes.option_id) FROM options 
    JOIN polls ON options.poll_id = polls.id
    JOIN votes ON options.id = votes.option_id
    WHERE poll_id = %s
    GROUP BY options.id
;"""
GET_POLL_TITLE = "SELECT title FROM polls WHERE id = %s;"

# -- Functions --

@contextmanager
def get_cursor(connection):
    with connection:
        with connection.cursor() as cursor:
            yield cursor


def create_tables(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(CREATE_POLLS_TABLE)
        cursor.execute(CREATE_POLL_OPTIONS_TABLE)
        cursor.execute(CREATE_VOTES_TABLE)

# -- Polls --

def create_poll(connection, poll_title: str, owner: str):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_POLL_RETURN_ID, (poll_title, owner))
        poll_id = cursor.fetchone()[0]
        return poll_id


def get_poll_title(connection, poll_id):
    with get_cursor(connection) as cursor:
        cursor.execute(GET_POLL_TITLE, (poll_id, ))
        return cursor.fetchone()[0]


def get_polls(connection) -> List[Poll]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_ALL_POLLS)
        return cursor.fetchall()


def get_poll(connection, poll_id: int) -> Poll:
    """Poll Type = Tuple[int, str, int] and not the Models class Poll"""
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL, (poll_id,))
        return cursor.fetchone()


# -- Options --

def get_poll_options(connection, poll_id: int) -> List[Option]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
        return cursor.fetchall()


def get_option(connection, option_id: int) -> Option:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_OPTION, (option_id,))
        return cursor.fetchone()


def add_option(connection, option_text: str, poll_id: int) -> Option:
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_OPTION_RETURN_ID, (option_text, poll_id))
        option_id = cursor.fetchone()[0]
        return option_id


# -- Votes --

def add_vote(connection, username: str, vote_timestamp: float, option_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_VOTE, (username, option_id, vote_timestamp))


def get_votes_for_option(connection, option_id: int) -> List[Vote]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_VOTES_FOR_OPTION, (option_id, ))
        return cursor.fetchall()


def get_latest_poll(connection) -> Poll:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_LATEST_POLL)
        cursor.fetchone()


# -- Chart --

def get_polls_vote_count(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLLS_VOTE_COUNT)
        return cursor.fetchall()


def get_poll_option_votes(connection, poll_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL_OPTION_VOTES, (poll_id, ))
        return cursor.fetchall()
