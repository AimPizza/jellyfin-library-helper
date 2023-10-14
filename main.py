import sys
from imdb import Cinemagoer
import os
import re


def MakeStrFromMovie(movieObj):
    return movieObj['title'] + " " + "(" + str(movieObj['year']) + ") " + "[imdbid-tt" + str(movieObj.getID()) + "]"

def GetDir():
    while True:
        directory = input("path: ")
        if os.path.exists(directory) and os.path.isdir(directory):
            return directory
        else:
            print("error with your directory, try again")

def PopulateContent(directory_path):
    return os.listdir(directory_path)

# TODO: make a selection of multiple but not all possible
# TODO: make reselection of directory possible after finding empty dir
def ChooseFromContent():
    all_valid_indicies = []

    for i, name in enumerate(content):
        if not re.findall(r'\[imdbid-', name):
            print(i, ": ", name)
            all_valid_indicies.append(i)

    if not all_valid_indicies:
        print("nothing found in this directory")
        sys.exit()
    else:
        print("a: all")
        print("q: quit")


    while True:
        choice = input("the choice is yours: ")
        if choice == "q":
            sys.exit()
        elif choice == "a":
            return all_valid_indicies
        elif choice.isdigit() and int(choice) in all_valid_indicies:
            return int(choice)
        else:
            print("invalid input, try again")

def Renamer(old_name, desired_name):
    original_path = os.path.join(base_directory, old_name)
    desired_path = os.path.join(base_directory, desired_name)
    os.rename(original_path, desired_path)


def ProcessMovies(indicies):
    if isinstance(indicies, int):
        name = content[int(indicies)]
        print("processing: ",name)
        rx_movie = ia.search_movie(name, results=1)
        finished_name = MakeStrFromMovie(rx_movie[0])
        print("check: ",BASE_URL+rx_movie[0].getID())
        Renamer(name, finished_name)
    elif isinstance(indicies, list):
        for i, index in enumerate(indicies):
            name = content[int(index)]
            print("processing: ",name)
            rx_movie = ia.search_movie(name, results=1)
            finished_name = MakeStrFromMovie(rx_movie[0])
            print("check: ",BASE_URL+rx_movie[0].getID())
            Renamer(name, finished_name)
    else:
        print("unknown argument to be processed")

    print("everything has been processed")

"""
---------------------------------------------------------
"""

BASE_URL = "https://www.imdb.com/title/tt"
ia = Cinemagoer()
base_directory = GetDir()
content = PopulateContent(base_directory)

selection_of_movies = ChooseFromContent()
ProcessMovies(selection_of_movies)
