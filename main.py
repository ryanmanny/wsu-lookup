from argparse import ArgumentParser
import asyncio

from src.wsu import get_student_by_id

parser = ArgumentParser(description='Retrieves student from WSU ID')
parser.add_argument('ids', nargs='+', help="one or more WSU IDs")


def main():
    for arg in parser.parse_args().ids:
        print(f"Processing {arg}")
        student = asyncio.run(get_student_by_id(arg))
        print(f"Found {student}")


if __name__ == '__main__':
    main()
