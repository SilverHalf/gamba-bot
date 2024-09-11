import sqlite3
import os
from gamble import Gamble
from functools import wraps

def query(f):
    '''
    Decorator for simple functions consisting in a single
    query that doesn't need to return results.
    '''
    @wraps(f)
    def wrapper(*args):
        conn = args[0]
        assert isinstance(conn, Connector)
        query = f(*args)
        conn._run_query(query, False)
    
    return wrapper

class Connector:

    def __init__(self, dbfile: str = 'gambadata.db'):

        filepath = os.path.join(os.path.dirname(__file__), dbfile)
        self._connection = sqlite3.connect(filepath)
        self._connection.autocommit = True

    @query
    def save_gamble(self, table: str, gamble: Gamble):
        '''Saves a gamble as a row in the specified table.'''

        return f"""
        INSERT INTO {table} VALUES
            (\'{gamble.user}\', {gamble.hands}, {gamble.gold}, {gamble.ectos}, {gamble.runes}, {gamble.timestamp})
        """

    @query
    def create_table(self, tablename: str):
        
        return f"CREATE TABLE {tablename}(player, gambles, gold, ectos, runes, timestamp)"

    def check_table_exists(self, tablename: str) -> bool:

        query = f'SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'{tablename}\';'
        return any(self._run_query(query))
        

    def _run_query(self, query: str, get_result: bool = True) -> list | None:
        '''
        Creates a cursor and attempts to run a query.
        If `get_result` is `True`, attempts to return the query results as a list.
        '''

        cursor = self._connection.cursor()
        result = cursor.execute(query)
        if get_result:
            result = result.fetchall()
        cursor.close()

        if get_result:
            return result
        return None
        
if __name__ == "__main__":
    conn = Connector("test.db")
    print(conn.check_table_exists('testguild'))
    conn.create_table("testguild")
    gam = Gamble("testuser")
    conn.save_gamble('testguild', gam)
    input("Press enter to conclude")
    conn._run_query("DROP TABLE testguild")
