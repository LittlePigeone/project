import sqlite3


class DataBase:
    def __init__(self, path_to_db, db_name):
        self.__connect = sqlite3.connect(str(path_to_db / db_name))
        self.__create_db()

    def __create_db(self):
        cursor = self.__connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS binding (
        id INTEGER PRIMARY KEY,
        path TEXT,
        name VARCHAR(40),
        key INTEGER)''')
        self.__connect.commit()

    def create(self, data: dict) -> int:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())

        cursor = self.__connect.cursor()
        cursor.execute('''INSERT INTO binding ({columns}) 
        VALUES ({placeholders})'''.format(columns=columns, placeholders=placeholders), values)
        self.__connect.commit()

        return cursor.lastrowid

    def get(self) -> list:
        cursor = self.__connect.cursor()
        cursor.execute('SELECT * FROM binding')
        self.__connect.commit()
        data = cursor.fetchall()
        return data

    def update(self, data: dict):
        if data.get('id', False):
            id = data.pop('id')
            fields = ', '.join([f'{key} = ?' for key in data.keys()])
            values = tuple(data.values())

            cursor = self.__connect.cursor()
            cursor.execute('''UPDATE binding SET {fields} 
            WHERE id = {id}'''.format(fields=fields, id=id), values)
            self.__connect.commit()
        else:
            return False

    def __del__(self):
        self.__connect.close()