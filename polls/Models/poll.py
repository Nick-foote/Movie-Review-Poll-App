from typing import List
from connection_pool import get_connection
from polls import poll_database
from polls.Models.option import Option


class Poll:
    """"""
    def __init__(self, title: str, owner: str, _id: int = None):
        self.title = title
        self.owner = owner
        self.id = _id

    def __repr__(self):
        return f"Poll({self.title!r}, {self.owner!r}, {self.id!r})"

    def save(self):
        with get_connection() as connection:
            new_poll_id = poll_database.create_poll(connection, self.title, self.owner)
            self.id = new_poll_id

    def add_option(self, option_text: str):
        Option(option_text, self.id).save()     # poll.id


    @property
    def options(self) -> List[Option]:
        with get_connection() as connection:
            options = poll_database.get_poll_options(connection, self.id)
            return [Option(option[1], option[2], option[0]) for option in options]
            # returns (option_text, poll_id, id)


    @classmethod
    def get(cls, poll_id: int) -> "Poll":
        """finds poll from poll id"""
        with get_connection() as connection:
            poll = poll_database.get_poll(connection, poll_id)
            # returns poll.id, poll.title, poll.owner
            return cls(poll[1], poll[2], poll[0])


    @classmethod
    def all(cls) -> List["Poll"]:
        """retrieves all polls created, in multiple rows"""
        with get_connection() as connection:
            polls = poll_database.get_polls(connection)
            return [cls(poll[1], poll[2], poll[0]) for poll in polls]
            # return (poll title, poll owner, poll id)


    @classmethod
    def latest(cls) -> "Poll":
        """retrieves latest poll created"""
        with get_connection() as connection:
            poll = poll_database.get_latest_poll(connection)
            return cls(poll[1], poll[2], poll[0])
