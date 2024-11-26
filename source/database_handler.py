import sqlite3


class DatabaseHandler:
    def __init__(self, db_path):
        self.database_path = db_path

    def get_phases(self):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, sequence FROM phases')
            return cursor.fetchall()

    def get_factions(self):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM factions')
            return cursor.fetchall()

    def get_faction(self, faction_id):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT name, color FROM factions WHERE id = \"{faction_id}\"')
            return cursor.fetchall()
