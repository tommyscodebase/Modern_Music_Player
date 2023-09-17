import os
import sqlite3

database_dir = os.path.join(os.getcwd(), '.dbs')
app_database = os.path.join(os.path.join(database_dir, 'app_db.db'))


# Create the database or a database table
def create_database_or_database_table(table_name: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (song TEXT)""")
    connection.commit()
    connection.close()


def add_song_to_database_table(song, table, database=app_database):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(f"""INSERT INTO {table} VALUES (?)""", (song,))
    connection.commit()
    connection.close()


def delete_song_from_database_table(song, table, database=app_database):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        f"""
        DELETE FROM favourites WHERE ROWID = (
            SELECT MIN(ROWID)
            FROM favourites WHERE song = '{song}'
        );
    """
    )
    connection.commit()
    connection.close()


def delete_all_songs_from_database_table(table, database=app_database):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        f"""DELETE FROM {table}"""
    )
    connection.commit()
    connection.close()


def fetch_all_songs_from_database_table(table, database=app_database):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(
        f"""SELECT song FROM {table}"""
    )
    song_data = cursor.fetchall()
    data = [song[0] for song in song_data]
    connection.commit()
    connection.close()

    return data
