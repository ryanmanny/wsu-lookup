from argparse import ArgumentParser
import asyncio

from src.wsu import get_student_by_id

parser = ArgumentParser(description="Retrieves student from WSU ID")
parser.add_argument('ids', nargs='+', help="one or more WSU IDs")
parser.add_argument('--quiet', action='store_true')


def main():
    args = parser.parse_args()
    for _id in args.ids:
        print(f"Processing {_id}")
        student = asyncio.run(get_student_by_id(_id, args.quiet))
        print(f"Found {student}")


if __name__ == '__main__':
    main()
