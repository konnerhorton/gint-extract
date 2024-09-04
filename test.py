import pandas as pd

from gint_extract import database

db = database.GintDatabase(r"assets/test_gint.gpj")
# db.write_all_tables_to_sqlite("db.sqlite")
db.write_tables_to_csv(r"csv")
