import argparse
import os
import sys

from gint_extract.database import GintDatabase


def main():
    parser = argparse.ArgumentParser(description="A simple CLI tool")
    parser.add_argument("file_path", help="Path to the file")
    parser.add_argument("--dir", help="output directory", default="csv")
    parser.add_argument(
        "--format", help="output format, either `csv` or `sqlite`", default="csv"
    )
    args = parser.parse_args()
    db = GintDatabase(args.file_path)
    if args.format == "csv":
        db.write_all_tables_to_csv(args.dir)
    elif args.format == "sqlite":
        db.write_all_tables_to_sqlite(args.dir)


if __name__ == "__main__":
    main()
