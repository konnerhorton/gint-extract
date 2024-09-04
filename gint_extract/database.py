import os
import warnings

import pandas as pd
import pyodbc
from sqlalchemy import create_engine

from gint_extract.vars import SYSTEM_TABLES

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")


def check_dir(dir_path):
    """
    Check if a directory exists, and create it if it does not.

    Parameters
    ----------
    dir_path : str
        The path to the directory to check or create.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class GintDatabase:
    """
    A class for interacting with a gINT database (Access format) and exporting its tables.

    Parameters
    ----------
    file_path : str
        The path to the gINT database file (.mdb or .accdb).

    Attributes
    ----------
    connStr : str
        The connection string used to connect to the Access database.
    cnxn : pyodbc.Connection
        The active connection to the database.
    cursor : pyodbc.Cursor
        The cursor object for executing queries in the database.
    table_names : list of str
        A list of all table names in the database excluding system tables.
    non_empty_tables : list of str
        A list of non-empty table names in the database.

    Methods
    -------
    get_table(table)
        Retrieves the content of a table as a pandas DataFrame.
    table_length(table)
        Returns the number of rows in a given table.
    write_table_to_csv(table, directory)
        Writes the content of a table to a CSV file.
    dfs()
        Returns a dictionary of non-empty tables as pandas DataFrames.
    write_all_tables_to_csv(directory)
        Writes all non-empty tables in the database to CSV files in the specified directory.
    write_table_to_sqlite(table, sqlite_conn)
        Writes the content of a table to an SQLite database.
    write_all_tables_to_sqlite(destination_path)
        Writes all non-empty tables to an SQLite database at the specified path.
    """

    def __init__(self, file_path):
        """
        Initialize the GintDatabase object and connect to the database.

        Parameters
        ----------
        file_path : str
            Path to the gINT database file (.mdb or .accdb).
        """
        self.connStr = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" r"DBQ=%s;" % file_path
        )
        self.file_path = file_path
        self.cnxn = pyodbc.connect(self.connStr)
        self.cursor = self.cnxn.cursor()
        try:
            self.table_names = [
                row.table_name
                for row in self.cursor.tables()
                if row.table_name not in SYSTEM_TABLES
            ]
            self.non_empty_tables = [
                table for table in self.table_names if self.table_length(table) > 0
            ]
        except Exception as e:
            print(f"Failed to load database with {e}")

    def get_table(self, table):
        """
        Retrieves the content of a table as a pandas DataFrame.

        Parameters
        ----------
        table : str
            The name of the table to retrieve.

        Returns
        -------
        pd.DataFrame
            The content of the table as a DataFrame.
        """
        sql = f"SELECT * FROM [{table}]"
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", message="pandas only supports SQLAlchemy connectable"
            )
            return pd.read_sql(sql, self.cnxn)

    def table_length(self, table):
        """
        Returns the number of rows in a given table.

        Parameters
        ----------
        table : str
            The name of the table to get the row count for.

        Returns
        -------
        int
            The number of rows in the table.
        """
        sql = f"SELECT * FROM [{table}]"
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", message="pandas only supports SQLAlchemy connectable"
            )
            return len(pd.read_sql(sql, self.cnxn))

    def write_table_to_csv(self, table, directory):
        """
        Writes the content of a table to a CSV file in the specified directory.

        Parameters
        ----------
        table : str
            The name of the table to export.
        directory : str
            The path to the directory where the CSV file will be saved.
        """
        check_dir(directory)
        self.get_table(table).to_csv(
            os.path.join(directory, f"{table}.csv"), index=False
        )

    def dfs(self):
        """
        Returns a dictionary of non-empty tables as pandas DataFrames.

        Returns
        -------
        dict of pd.DataFrame
            A dictionary where the keys are table names and values are DataFrames.
        """
        dataframes = {}
        for table in self.non_empty_tables:
            dataframes[table] = self.get_table(table)
        return dataframes

    def write_all_tables_to_csv(self, directory):
        """
        Writes all non-empty tables in the database to CSV files in the specified directory.

        Parameters
        ----------
        directory : str
            The path to the directory where the CSV files will be saved.
        """
        check_dir(directory)
        for table in self.non_empty_tables:
            self.write_table_to_csv(table, directory)

    def write_table_to_sqlite(self, table, sqlite_conn):
        """
        Writes the content of a table to an SQLite database.

        Parameters
        ----------
        table : str
            The name of the table to export.
        sqlite_conn : sqlalchemy.engine.base.Connection
            The SQLite connection object.
        """
        df = self.get_table(table)
        df.to_sql(table, sqlite_conn, if_exists="replace", index=False)

    def write_all_tables_to_sqlite(self, destination_path):
        """
        Writes all non-empty tables to an SQLite database at the specified path.

        Parameters
        ----------
        destination_path : str
            The file path to the SQLite database where the tables will be saved.
        """
        sqlite_engine = create_engine(f"sqlite:///{destination_path}")
        with sqlite_engine.connect() as sqlite_conn:
            for table in self.non_empty_tables:
                self.write_table_to_sqlite(table, sqlite_conn)
