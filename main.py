"""Logic of Jellyfin-Library-Helper."""

import sys
from imdb import Cinemagoer
import os
import re
import argparse
from pathlib import Path
from enum import Enum
from typing import List


def make_str_from_movie(movieObj):
    print('movie object:')
    print(movieObj)
    return (
        movieObj['title']
        + ' '
        + '('
        + str(movieObj['year'])
        + ') '
        + '[imdbid-tt'
        + str(movieObj.getID())
        + ']'
    )


def assert_dir_valid(directory: Path) -> bool:
    """Perform simple checks on a path."""
    if (
        os.path.exists(directory)
        and os.path.isdir(directory)
        and os.access(directory, os.W_OK)
    ):
        pass
    else:
        print('error with your directory, please troubleshoot')
        sys.exit(1)


# TODO: make a selection of multiple but not all possible
def choose_from_directory(content: List[str]):
    """Filter, list and give choice based on filenames."""
    relevant_entries = []

    # exclude files that already have an imdbid
    for i, name in enumerate(content):
        if not re.findall(r'\[imdbid-', name):
            print(i, ': ', name)
            relevant_entries.append(i)

    if len(relevant_entries) == 0:
        print('nothing found in this directory')
        sys.exit()
    else:
        print('a: all')
        print('q: quit')

    while True:
        choice = input('the choice is yours: ')
        if choice == 'q':
            sys.exit()
        elif choice == 'a':
            return relevant_entries
        elif choice.isdigit() and int(choice) in relevant_entries:
            return int(choice)
        else:
            print('invalid input, try again')


def rename(old_name, desired_name):
    """Rename a file by specifying only the name.

    The base directory is assumed by the global constant
    """
    original_path = os.path.join(LIB_PATH, old_name)
    desired_path = os.path.join(LIB_PATH, desired_name)
    os.rename(original_path, desired_path)


def get_media(content: List[str], index: int):
    name = content[int(index)]
    print('processing: ', name)
    rx_media = CINEMA.search_movie(name, results=1)
    rx_movie = CINEMA.get_movie(rx_media[0].movieID)
    finished_name = make_str_from_movie(rx_movie)
    print('check: ', BASE_URL + rx_movie.getID())
    confirmation = input('Do you want to rename this file? (y/N): ').strip().lower()
    if confirmation == 'y' or confirmation == 'yes':
        rename(name, finished_name)
    else:
        print('Renaming skipped.')


def process_media(content: List[str], indicies):
    """Handle media based on the dir contents and the selection.

    `indicies` may actually be a single index
    """
    if isinstance(indicies, int):
        get_media(content, index=indicies)  # sorry for ambigous naming
    elif isinstance(indicies, list):
        for index in indicies:
            get_media(content, index)
    else:
        print('unknown argument to be processed')

    print('everything has been processed')


def parse_args():
    """Handle arguments."""
    parser = argparse.ArgumentParser(
        description='Lookup directories of your Jellyfin library'
    )

    main_group = parser.add_mutually_exclusive_group(required=True)
    main_group.add_argument(
        '-m', '--movies', action='store_true', help='Look for movies'
    )
    main_group.add_argument(
        '-s', '--shows', action='store_true', help='Look for series/shows'
    )

    parser.add_argument(
        '-p',
        '--path',
        required=True,
        type=Path,
        default=None,
        help='Path to your specific library',
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f'Error: path is not a valid directory: {args.path}', file=sys.stderr)
        sys.exit(1)

    return args


# TODO: unused
class MEDIA_TYPE(Enum):
    """Enum for possible types of media."""

    MOVIES = 1
    SHOWS = 2


"""
---------------------------------------------------------
"""

BASE_URL = 'https://www.imdb.com/title/tt'
TYPE = None
LIB_PATH = None
CINEMA = None  # Cinemagoer object


def main():
    global LIB_PATH, TYPE, CINEMA
    CINEMA = Cinemagoer()

    args = parse_args()

    if args.movies:
        TYPE = MEDIA_TYPE.MOVIES
    elif args.shows:
        TYPE = MEDIA_TYPE.SHOWS

    LIB_PATH = args.path.resolve()

    assert_dir_valid(LIB_PATH)

    dir_content = os.listdir(LIB_PATH)

    selection_of_movies = choose_from_directory(dir_content)
    process_media(dir_content, selection_of_movies)


if __name__ == '__main__':
    main()
