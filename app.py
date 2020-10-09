from movies import movie_functions
from polls import poll_functions

WELCOME = "Welcome to my movie review and poll database"

START_MENU = """
Would you like to look up movies reviews or on movie polls:
    
    1) Look up a movie to read/write a movie review, or watch trailer
    2) Answer a movie poll and view results
    
    Or press Enter to exit
    
Your selection:
"""


while len(menu_option := input(START_MENU)) != 0:
    if menu_option == "1":
        movie_functions.menu_movie()
    elif menu_option == "2":
        poll_functions.menu_poll()
    else:
        print("Invalid command, please try again")

print("Exiting movie database")
