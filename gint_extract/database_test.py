import os
import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gint_extract.database import GintDatabase


@pytest.fixture
def mock_db():
    with patch("database.pyodbc.connect") as mock_connect:
        # Mock the database connection and cursor
        mock_cnxn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_cnxn
        mock_cnxn.cursor.return_value = mock_cursor

        # Mock the tables method to return some table names
        mock_cursor.tables.return_value = [
            MagicMock(table_name="table1"),
            MagicMock(table_name="table2"),
        ]

        # Mock the SYSTEM_TABLES to exclude system tables
        global SYSTEM_TABLES
        SYSTEM_TABLES = []

        # Mock the read_sql method to return a DataFrame
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        pd.read_sql = MagicMock(return_value=mock_df)

        # Initialize the GintDatabase object
        db = GintDatabase("test_path")
        yield db


def test_initialization(mock_db):
    assert mock_db.file_path == "test_path"
    assert mock_db.table_names == ["table1", "table2"]
    assert mock_db.non_empty_tables == ["table1", "table2"]


def test_table_length(mock_db):
    assert mock_db.table_length("table1") == 2


def test_get_table(mock_db):
    df = mock_db.get_table("table1")
    assert df.equals(pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}))


def test_write_table_to_csv(mock_db, tmpdir):
    directory = tmpdir.mkdir("sub")
    mock_db.write_table_to_csv("table1", str(directory))
    assert os.path.exists(os.path.join(directory, "table1.csv"))


def test_write_tables_to_csv(mock_db, tmpdir):
    directory = tmpdir.mkdir("sub")
    mock_db.write_tables_to_csv(str(directory))
    assert os.path.exists(os.path.join(directory, "table1.csv"))
    assert os.path.exists(os.path.join(directory, "table2.csv"))
