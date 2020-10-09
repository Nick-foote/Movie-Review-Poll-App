import datetime
from typing import List
import pytz

from polls import poll_database
from connection_pool import get_connection


## need to complete comments for Option.py and Poll.py
class Option:
    def __init__(self, options_text: str, poll_id: int, _id: int = None):
        self.id = _id
        self.text = options_text
        self.poll_id = poll_id

    def __repr__(self):
        return f"Option({self.text!r}, {self.poll_id!r}, {self.id!r})"

    def save(self):
        with get_connection() as connection:
            new_option_id = poll_database.add_option(connection, self.text, self.poll_id)
            self.id = new_option_id

    @classmethod
    def get(cls, option_id: int) -> "Option":
        with get_connection() as connection:
            option = poll_database.get_option(connection, option_id)
            return cls(option[1], option[2], option[0])

    def vote(self, username: str, ):
        with get_connection() as connection:
            current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
            current_timestamp: float = current_datetime_utc.timestamp()
            poll_database.add_vote(connection, username, current_timestamp, self.id)

    #  Retrieves Tuple(votes.username, votes.option_id)
    @property
    def votes(self) -> List[poll_database.Vote]:
        with get_connection() as connection:
            votes = poll_database.get_votes_for_option(connection, self.id)
            return votes

