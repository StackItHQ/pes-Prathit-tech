import mysql.connector
from mysql.connector import Error

class DatabaseListener:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = self._connect()
        self.cursor = self.connection.cursor()
        self.last_known_state = self._get_current_state()

    def _connect(self):
        try:
            connection = mysql.connector.connect(**self.db_config)
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error: {e}")
        return None

    def _get_current_state(self):
        self.cursor.execute("SELECT * FROM your_table")
        return self.cursor.fetchall()

    def get_changes(self):
        current_state = self._get_current_state()
        changes = []
        for i, row in enumerate(current_state):
            if i >= len(self.last_known_state) or row != self.last_known_state[i]:
                changes.append(('update', i, row))
        for i in range(len(current_state), len(self.last_known_state)):
            changes.append(('delete', i, None))
        self.last_known_state = current_state
        return changes

    def __del__(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()