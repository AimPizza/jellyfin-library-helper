"""Logic of Jellyfin-Library-Helper."""

import sys
from imdb import Cinemagoer
import os
import re
import argparse
from pathlib import Path
from enum import Enum
from typing import List

BASE_URL = 'https://www.imdb.com/title/tt'
TYPE = None
LIB_PATH = None
CINEMA = None  # Cinemagoer object


def format_to_movie_template(title, release_year, id):
    """Format given data points to movie template."""
    return title + ' ' + '(' + release_year + ') ' + '[imdbid-tt' + str(id) + ']'


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
            print('quitting..')
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


# TODO: imdb does not work well for shows unfortunately
def query_from_multiple_entries(name: str) -> int:
    """Query for a given name and return its ID on a db."""
    rx_media = CINEMA.search_movie(name, results=5)
    if TYPE == MEDIA_TYPE.MOVIES:
        for index, movie in enumerate(rx_media):
            if movie['kind'] != 'tv series':
                print(f'{index}: {movie["title"]}')
    # TODO: implement shows
    elif TYPE == MEDIA_TYPE.SHOWS:
        pass

    if not rx_media:
        print('found nothing :[ (try another name)')
        sys.exit(1)

    chosen_movie_index = int(input('please choose one: '))
    return rx_media[chosen_movie_index].movieID


def confirm_processing(original_name: str, final_name: str, media_obj):
    """Ask for confirmation and handle changes before renaming."""
    # TODO: handle differences between movies and shows (on the media_obj)
    print(f"""please check:
    - url: {BASE_URL + media_obj.getID()}
    - final form: {final_name}""")
    confirmation = input('Do you want to rename this file? (y/N/c): ').strip().lower()
    if confirmation == 'y' or confirmation == 'yes':
        rename(original_name, final_name)
    elif confirmation == 'c' or confirmation == 'change':
        final_name = input('manual input: ')
        rename(original_name, final_name)
    else:
        print('Renaming skipped.')


# TODO: features that allow speed-processing (full automatic, accepting first entry)
def handle_media(folder_name: str):
    """Look up a specific media title and rename directory."""
    print('processing: ', folder_name)
    id_to_look_up = query_from_multiple_entries(folder_name)
    rx_media = CINEMA.get_movie(id_to_look_up)
    finished_name = format_to_movie_template(
        rx_media['title'], str(rx_media['year']), rx_media.getID()
    )

    confirm_processing(
        original_name=folder_name, final_name=finished_name, media_obj=rx_media
    )


def init_processing(content: List[str], indicies):
    """Handle media based on the dir contents and the selection.

    `indicies` may actually be a single index
    """
    if isinstance(indicies, int):
        index = indicies  # sorry for ambigous naming
        handle_media(content[index])
    elif isinstance(indicies, list):
        for index in indicies:
            handle_media(content[index])
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


def main():
    """Run the main logic."""
    global LIB_PATH, TYPE, CINEMA
    CINEMA = Cinemagoer()

    args = parse_args()

    if args.movies:
        TYPE = MEDIA_TYPE.MOVIES
    elif args.shows:
        TYPE = MEDIA_TYPE.SHOWS
        # TODO
        print(
            'Shows-functionality not properly implemented yet. Please try with passing -m or do manually.'
        )
        sys.exit(0)

    LIB_PATH = args.path.resolve()

    assert_dir_valid(LIB_PATH)

    dir_content = os.listdir(LIB_PATH)

    selection_of_movies = choose_from_directory(dir_content)
    init_processing(dir_content, selection_of_movies)


if __name__ == '__main__':
    main()
