import datetime
import random
from typing import List
import pytz
import matplotlib.pyplot as plt
from connection_pool import get_connection
from polls import poll_database, charts
from polls.Models.option import Option
from polls.Models.poll import Poll


POLL_MENU = """\nPlease pick an option:

    1) Create new poll
    2) List open polls
    3) Vote on a poll
    4) Show poll votes 
    5) Select a random vote as a winner (tbc if value)
    6) View a bar chart of votes counts on all polls
    7) Select a poll to make into a pie chart

    Or press Enter to go back
  
Your selection:   
"""

NEW_OPTION_PROMPT = "Enter a new option text (or leave empty to stop adding options): "


# -- Functions --

def prompt_create_poll():
    """Creates new poll title, owner and poll options in function"""
    poll_title = input("Enter the poll title: ")
    poll_owner = input("Enter who is the poll owner: ")
    poll = Poll(poll_title, poll_owner)
    poll.save()

    while new_option := input(NEW_OPTION_PROMPT):       # adding options to the new poll
        poll.add_option(new_option)


def list_open_polls():
    for poll in Poll.all():
        print(f"{poll.id}: {poll.title} (created by {poll.owner})")


def prompt_vote_poll():
    poll_id = int(input("Enter the poll id you want to vote on: "))

    _print_poll_options(Poll.get(poll_id).options)      #passing list of poll options

    option_id = int(input("Enter the option id you want to vote for: "))
    username = input("Enter the username you want to vote as: ")
    Option.get(option_id).vote(username)



def _print_poll_options(options: List[Option]):
    """this Option use is the Option class and not the tuple above.
    Let's we can print the class attributes"""
    for option in options:
        print(f"{option.id}: {option.text}")


def show_poll_votes():
    poll_id = int(input("Enter the poll id you want to see votes for: "))
    poll = Poll.get(poll_id)
    options = poll.options

    votes_per_option = [len(option.votes) for option in options]
    total_votes = sum(votes_per_option)

    try:
        print("-- Poll votes --")
        # zip() function to aggregate tuples crossing over values.
        for option, votes in zip(options, votes_per_option):
            percentage = votes / total_votes * 100
            print(f"{option.text}: {votes} votes   ({percentage:.2f}%)")
    except ZeroDivisionError:
        print("This poll has no votes yet")

    vote_log = input("\nWould you like to see the vote log? (y/N) ")


    if vote_log == "y":     # retrieves username and timecode for each vote
        _print_votes_for_options(options)


def _print_votes_for_options(options: List[Option]):
    for option in options:
        print(f"{option.text}:")
        for vote in option.votes:       # convert from timestamp to London time
            native_datetime = datetime.datetime.utcfromtimestamp(vote[2])
            utc_date = pytz.utc.localize(native_datetime)
            local_date = utc_date.astimezone(pytz.timezone("Europe/London"))
            local_date_as_str = local_date.strftime( "%Y-%m-%d %H:%M")
            print(f"\t{vote[0]} at {local_date_as_str}")


def randomise_poll_winner():
    """selects a random voted option row, from a chosen poll & option"""
    poll_id = int(input("Enter a poll id you want to select a winner from: "))
    poll = Poll.get(poll_id)
    _print_poll_options(poll.options)

    option_id = int(input("Enter an option id you want to select a winner from: "))
    votes = Option.get(option_id).votes
    winner = random.choice(votes)
    print(f"The randomly selected winner is '{winner[0]}'")


def _chart_options_for_poll(poll_id: int):
    with get_connection() as connection:
        options = poll_database.get_poll_option_votes(connection, poll_id)

        figure = charts.get_pie_chart(options)
        plt.show()


def prompt_select_poll():
    with get_connection() as connection:
        polls = poll_database.get_polls(connection)
        print("-- Polls --")
        for poll in polls:
            print(f"{poll[0]}: {poll[1]}")

        selected_poll = int(input("Enter poll id to create a pie chart: "))
        _chart_options_for_poll(selected_poll)


def create_polls_bar_chart():
    with get_connection() as connection:
        polls = poll_database.get_polls_vote_count(connection)
        charts.create_polls_bar_chart(polls)
        plt.show()


# -- Menu --

# mapping numbers to functions. Not calling the functions however.
MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomise_poll_winner,
    "6": create_polls_bar_chart,
    "7": prompt_select_poll,
}

def menu_poll():
    with get_connection() as connection:
        poll_database.create_tables(connection)

    while len(selection := input(POLL_MENU)) != 0:
        try:
            MENU_OPTIONS[selection]()       # turns the menu mapped value into a function()
        except KeyError:
            print("Invalid input selected. Please try again.")
