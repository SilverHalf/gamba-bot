import sqlite3
import os
from gamble import Gamble
from functools import wraps

def simple_query(f):
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

def gamble_query(f):
    '''
    Decorator for queries meant to build gamble objects.
    The query should build a set of rows, each one with the
    required data to build a Gamble object.
    This decorator will then build the object for each row
    and return all results as a list.
    '''
    @wraps(f)
    def wrapper(*args):
        conn = args[0]
        assert isinstance(conn, Connector)
        query = f(*args)
        gambles = []
        rows = conn._run_query(query)
        for row in rows:
            gambles.append(Gamble(*row))

        return gambles
    
    return wrapper

class Connector:
    '''
    Interface for the gambling sqlite database, which specifies
    several default queries and convenience functions.
    '''

    def __init__(self, dbfile: str = 'gambadata.db'):
        '''
        Creates a new Connector. The connector will automatically use the
        specified `dbfile` sqlite database, creating the file if it
        doesn't already exist.
        '''

        filepath = os.path.join(os.path.dirname(__file__), dbfile)
        self._connection = sqlite3.connect(filepath)

    @simple_query
    def save_gamble(self, table: str, gamble: Gamble):
        '''Saves a gamble as a row in the specified table.'''

        return f"""
        INSERT INTO {table} VALUES
            ({gamble.user}, {gamble.hands}, {gamble.gold}, {gamble.ectos}, {gamble.runes}, {gamble.timestamp})
        """
    
    @simple_query
    def remove_last_gamble(self, table: str, userid: int):
        '''Deletes the most recent entry by a user.'''

        return f'''
        DELETE FROM {table}
        WHERE player={userid}
        ORDER BY timestamp DESC
        LIMIT 1
        '''

    @simple_query
    def create_table(self, tablename: str):
        '''Creates a new table in the gambling database.'''
        
        return f"CREATE TABLE {tablename}(player, gambles, gold, ectos, runes, timestamp)"
    
    @gamble_query
    def user_totals(self, tablename: str, userid: int) -> list[Gamble]:
        '''Gets the sum data for a user within a table.'''

        return f'''
            SELECT player, SUM(gambles), SUM(gold), SUM(ectos), SUM(runes), MAX(timestamp)
            FROM {tablename}
            WHERE player={userid}
        '''
    @gamble_query
    def bot_totals(self, tablename: str) -> list[Gamble]:
        '''Gets the sum data for all users within a table.'''

        return f'''
            SELECT null, SUM(gambles), SUM(gold), SUM(ectos), SUM(runes), MAX(timestamp)
            FROM {tablename}
        '''
    
    @gamble_query
    def all_user_totals(self, tablename: str) -> list[Gamble]:

        return f'''
            SELECT player, SUM(gambles), SUM(gold), SUM(ectos), SUM(runes), MAX(timestamp)
            FROM {tablename}
            GROUP BY player
        '''
    
    @gamble_query
    def recent_by_user(self, tablename: str, userid: int, n: int) -> list[Gamble]:
        '''Gets the n most recent gambles by the user with the given id in the specified table.'''

        return f'''
            SELECT player, gambles, gold, ectos, runes, timestamp
            FROM {tablename}
            WHERE player={userid}
            ORDER BY timestamp DESC
            LIMIT {n}
        '''

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
        self._connection.commit()

        if get_result:
            return result
        return None
        
if __name__ == "__main__":
    conn = Connector("gambadata.db")
    g = Gamble(1234, 1, 200, 400, 1)
    conn.save_gamble('data', g)
    conn.remove_last_gamble('data', 1234)