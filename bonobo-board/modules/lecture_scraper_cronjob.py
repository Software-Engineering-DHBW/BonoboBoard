# -*- coding: utf-8 -*-

"""Solo-Script to be included in a cronjob in the docker-container. Scrapes all lectures and writes them to a database.
"""

from dhbw.lecture_importer import write_all_courses_lectures_to_database


def main():
    """Function to gather all timetables consecutively and write them to database.

    Returns
    -------
    None
    """
    write_all_courses_lectures_to_database()


if __name__ == "__main__":
    main()
