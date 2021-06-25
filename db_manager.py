import sqlite3


class DB_manager:
    def __init__(self):
        self.db = sqlite3.connect('Mail_tracking_bot.sqlite', check_same_thread=False)
        self.sql = self.db.cursor()

        self.sql.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT, position TEXT)")
        self.sql.execute(
            "CREATE TABLE IF NOT EXISTS files (file_id TEXT, uuid TEXT, channel_id INT, permission TEXT, downloads_count INT, unique_downloads INT, description TEXT)")
        self.db.commit()

    def update_user_position(self, user_id, position="None"):
        self.sql.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'")
        if not self.sql.fetchone():
            self.sql.execute(f"INSERT INTO users VALUES  (?,?)", (user_id, position))
            print("User added")
        else:
            self.sql.execute(f'UPDATE users SET position = "{position}" WHERE user_id = "{user_id}"')
        self.db.commit()

    def user_exist(self, user_id):
        self.sql.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'")
        return self.sql.fetchone()

    def get_user_position(self, user_id):
        self.sql.execute(f"SELECT position from users WHERE user_id = '{user_id}'")
        return self.sql.fetchone()

    def get_file_id(self, uuid):
        self.sql.execute(f"SELECT file_id FROM files WHERE uuid = '{uuid}'")
        return self.sql.fetchone()

    def add_file_id(self, file_id, uuid ):
        self.sql.execute(f"INSERT INTO files VALUES  ('{file_id}', '{uuid}')")
        self.db.commit()

    def debug_info(self):
        self.sql.execute(f"SELECT * from users")
        print(self.sql.fetchall())
