# External Libraries
import os
import sqlite3
import pandas as pd

# Models
from models.scrape_model import ScrapeState

# Internal Libraries
from data_sources.ProFootballReference import ProFootballReference

# Utilities
from utils.logger import log

# Set variables that will need to be accessed
this_filename = os.path.basename(__file__).replace(".py","")
log_path = None
log_type = None
db_path = None

def db_and_table_exists(conn, db: str, table: str) -> bool:
    """
    Return True if table is a table that already exists in the database.

    Accepts a SQLite3 connection, the path to the database, and the name of the table
    """

    # Check if the database esxists
    if not os.path.isfile(db):
        return False
    
    # Check if the table exists
    cur = conn.cursor()
    cur.execute(
        """SELECT name FROM sqlite_master WHERE type="table" AND name=?""", [table]
    )
    if cur.fetchone() is None:
        return False
    
    # Close the connection and return
    cur.close()
    return True

def get_update_query(table: str, col_strings: dict):
    """Generates the query that will update a table for existing records"""
    update_query = f"""
        UPDATE { table }
        SET { col_strings['update_cols_string'] }
        { col_strings['where_string'] 
    }"""
    
    return update_query

def get_column_strings(key_col: str, all_cols: list, table: str):
    """
    Generates a list of strings needed for the update query.
    
    Takes a list of primary keys, a list of all columns, and the name of the table.
    """
    update_cols_string = ",\n".join(f"{ col } = (SELECT { col } FROM tmp_{ table } WHERE tmp_{ table }.{ key_col } = { table }.{ key_col })" for col in all_cols if col not in ['event_id','team'])
    if table == "team_result": 
        where_string = f"WHERE EXISTS (SELECT 1 FROM tmp_{ table } WHERE tmp_{ table }.event_id = { table }.event_id and tmp_{ table }.team = { table }.team)"
    else:
        where_string = f"WHERE event_id IN (SELECT event_id FROM tmp_{ table })"
    return { 
        "update_cols_string": update_cols_string,
        "where_string": where_string
    }

def get_existing_ids(conn, table: str):
    """
    Gets existing event_ids from a table. Checks if the table exists first.

    Takes a connection and the name of the table.
    """
    table_query = f"""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='{ table }';
    """
    event_id_query = "SELECT event_id FROM event"
    cur = conn.cursor()
    cur.execute(table_query)
    table_exists = cur.fetchone()
    if table_exists:
        cur.execute(event_id_query)
        rows = cur.fetchall()
        cur.close()
        event_ids = [row[0] for row in rows]
        return event_ids
    return []

def create_insert_or_update_table(
        conn, 
        table: str, 
        df: pd.DataFrame, 
        key_col: str
    ):
    """
    Will CREATE, INSERT INTO, and/or UPDATE a table.

    Takes a connection, the name of the table, a dataframe of rows to be inserted or updated
    """
    existing_ids = get_existing_ids(conn, table)
    mask_in = df[key_col].isin(existing_ids) # New concept, create a mask
    existing_rows = df[mask_in] # Use it
    mask_not_in = ~mask_in # Reverse it
    new_rows = df[mask_not_in]

    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS tmp_{ table };")
    conn.commit()

    if not db_and_table_exists(conn, db_path, table):
        df.to_sql(table, conn, index=False)
    else:
        # Create a temp table with the existing rows
        count = existing_rows.to_sql(f"tmp_{ table }", conn, index = False)
        log(log_path,f"{count} rows inserted in tmp_{ table }", log_type, this_filename)
        
        # Insert the new rows
        count = new_rows.to_sql(table, conn, if_exists = "append", index = False)
        log(log_path,f"{count} rows inserted in { table }", log_type, this_filename)

        # Then update existing rows from the temp table
        col_strings = get_column_strings(key_col, list(existing_rows.columns), table)
        update_query = get_update_query(table, col_strings)
        #print(update_query)
        cur.execute(update_query)
        conn.commit()
        cur.close()
        log(log_path, f"{ cur.rowcount } rows updated in { table }", log_type, this_filename)
                                       
def load_history_from_pfr(state: ScrapeState) -> ScrapeState:
    """Scrapes data from Pro Football Reference and loads to the database."""
    # Set global variable values
    global log_path, log_type, db_path
    log_path = state["log_path"]
    log_type = state["log_type"]
    db_path = state["db_path"]

    # Create or connect to the database
    log(state["log_path"], "Connecting to database...\n", state["log_type"], this_filename)
    conn = sqlite3.connect("db/historical_data.db")
    cur = conn.cursor()

    # Load data from Pro Football Reference
    pfr = ProFootballReference(state)
    data = pfr.get_data(state["seasons"])

    # Get the data in the database
    create_insert_or_update_table(conn, "event", data["events"], "event_id")
    create_insert_or_update_table(conn, "team_result", data["game_data"], "event_id")
    
    # Create primary keys if they don't exist
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_event_id
        ON event(event_id);
    """)
    
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_event_id_team_compound
        ON team_result(event_id, team);
    """)
    
    conn.commit()
    cur.close() 
    
    return state