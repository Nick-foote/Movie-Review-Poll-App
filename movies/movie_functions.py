import webbrowser
import datetime
from movies import movie_database
from connection_pool import get_connection

MOVIE_MENU = """Please select an option from the following:

    1) Add a new movie to the database
    2) View upcoming movies
    3) View all movies
    4) Search for a movie
    5) See reviews for a movie
    6) Write a movie review
    7) View your movie reviews
    8) View movie trailer
    9) Create a new user


    Or press Enter to go back

Your selection: """


# -- Functions --

def prompt_add_movie():
    """Release date is important so we can search upcoming films"""

    title = input("Movie Title: ")
    release_date = input("Release Date (dd-mm-yyyy): ")
    parsed_date = datetime.datetime.strptime(release_date, "%d-%m-%Y")
    timestamp = parsed_date.timestamp()
    trailer_url = input("Paste full trailer URL: ")
    with get_connection() as connection:
        movie_database.add_movie(connection, title, timestamp, trailer_url)


def prompt_add_user():
    username = input("Enter a username: ")
    with get_connection() as connection:
        movie_database.add_user(connection, username)


def prompt_upcoming_movies():
    with get_connection() as connection:
        movies = movie_database.get_movies(connection, True)
        print_movie_list("Upcoming", movies)


def prompt_movies():
    with get_connection() as connection:
        movies = movie_database.get_movies(connection)
        print_movie_list("All", movies)


def print_movie_list(heading, movies):
    print(f"-- {heading} movies --")
    for _id, title, release_date, _ in movies:
        movie_date = datetime.datetime.fromtimestamp(release_date)
        date_string = movie_date.strftime("%b %d %Y")
        print(f"{_id}: {title} ({date_string})")
    print("----\n")


def prompt_review_movie():
    """giving a film a review"""

    username = input("Username: ")
    # must enter film ID rather than title
    movie_id = input("Movie ID# ")
    review = input("Enter your review of the movie: ")
    with get_connection() as connection:
        movie_database.review_movie(connection, username, movie_id, review)


def prompt_search_movie():
    """finds any matches in the movie database based on whole
    or part of words from user input"""

    search_input = input("Enter part of a movie title to search: ")
    with get_connection() as connection:
        movies = movie_database.search_movie(connection, search_input)
        if movies:
            print_movie_list("Found", movies)
        else:
            print(f"No movies found with '{search_input}'")
        print("\n")



def prompt_movie_reviews():
    """returns all reviews for a movie from different users"""

    movie_id = input("Enter the Movie ID# ")
    with get_connection() as connection:
        movies = movie_database.get_movie_reviews(connection, movie_id)
        if movies:
            title = movies[0][0]
            print(f"Reviews for '{title}':")
            for _, username, review in movies:
                print(f'{username}: "{review}"')
        else:
            print(f"There are no reviews found")
        print("\n")


def prompt_get_reviewed():
    """returns multiple reviews of films the user has done"""

    username = input("username: ")
    with get_connection() as connection:
        movies = movie_database.get_reviewed_movies(connection, username)
    if movies:
        print_reviewed_list(username, movies)
    else:
        print(f"{username} has no reviewed movies")


def print_reviewed_list(username: str, movies):
    print(f"-- {username.capitalize()}'s reviewed movies --")
    for title, _, review in movies:
        print(f'{title}  - "{review}"')
    print("----\n")


def prompt_trailer_url():
    """opens the movie trailer on the default computer browser"""

    with get_connection() as connection:
        title = input("Enter movie title: ")
        url = movie_database.get_trailer_url(connection, title)

        try:
            webbrowser.open(url[0], new=0, autoraise=True)
        except Exception as e:
            print(e)


# -- Menu Set Up --

MENU_OPTIONS = {
    "1": prompt_add_movie,
    "2": prompt_upcoming_movies,
    "3": prompt_movies,
    "4": prompt_search_movie,
    "5": prompt_movie_reviews,
    "6": prompt_review_movie,
    "7": prompt_get_reviewed,
    "8": prompt_trailer_url,
    "9": prompt_add_user,
}


def menu_movie():
    with get_connection() as connection:
        movie_database.create_tables(connection)

    while len(selection := input(MOVIE_MENU)) != 0:
        try:
            MENU_OPTIONS[selection]()       # turns the menu mapped value into a function()
        except KeyError:
            print("Invalid command. Please try again.")
