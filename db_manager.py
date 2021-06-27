import sqlite3


class DB_manager:
    def __init__(self):
        self.db = sqlite3.connect('Mail_tracking_bot.sqlite', check_same_thread=False)
        self.sql = self.db.cursor()

        self.sql.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT, position TEXT, current_channel_id TEXT, selected_channel_id TEXT)")
        self.sql.execute("CREATE TABLE IF NOT EXISTS channels ( channel_id TEXT, channel_url TEXT)")
        self.sql.execute("CREATE TABLE IF NOT EXISTS downloads ( uuid TEXT, user_id TEXT)")
        self.sql.execute("CREATE TABLE IF NOT EXISTS messages (message_id TEXT, uuid TEXT, deep_linked_url TEXT)")
        self.sql.execute(
            "CREATE TABLE IF NOT EXISTS files (file_id TEXT, uuid TEXT, channel_id TEXT, channel_url TEXT, downloads INT, uniq_downloads INT, downloads_with_subscribe INT, downloads_with_new_subscribe, description TEXT)")
        self.db.commit()

    def update_user_position(self, user_id, position="", current_channel_id="", selected_channel_id=""):
        self.sql.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'")
        if not self.sql.fetchone():
            self.sql.execute(f"INSERT INTO users VALUES  (?,?,?,?)",
                             (user_id, position, current_channel_id, selected_channel_id))
            print("User added")
        else:
            if not position == "":
                self.sql.execute(f'UPDATE users SET position = "{position}" WHERE user_id = "{user_id}"')
            if not current_channel_id == "":
                self.sql.execute(
                    f'UPDATE users SET current_channel_id = "{current_channel_id}" WHERE user_id = "{user_id}"')
            if not selected_channel_id == "":
                self.sql.execute(
                    f'UPDATE users SET selected_channel_id = "{selected_channel_id}" WHERE user_id = "{user_id}"')

        self.db.commit()

    def get_if_download(self, user_id, uuid):
        self.sql.execute(f"SELECT user_id FROM downloads WHERE (uuid = '{uuid}' AND user_id = '{user_id}')")
        return self.sql.fetchone()

    def add_download(self, user_id, uuid):
        self.sql.execute(f"INSERT INTO downloads VALUES  ('{uuid}', '{user_id}')")

    def get_message_id(self, uuid):
        self.sql.execute(f"SELECT message_id FROM messages WHERE uuid = '{uuid}'")
        return self.sql.fetchone()[0]

    def get_message_deep_link(self, uuid):
        self.sql.execute(f"SELECT deep_linked_url FROM messages WHERE uuid = '{uuid}'")
        return self.sql.fetchone()[0]

    def update_message_id(self, uuid, message_id="", deep_linked_url=""):
        self.sql.execute(f"SELECT message_id FROM messages WHERE uuid = '{uuid}'")
        if not self.sql.fetchone():
            self.sql.execute(f"INSERT INTO messages VALUES  ('{message_id}', '{uuid}', '{deep_linked_url}')")
            print("Message added")
        else:
            self.sql.execute(f'UPDATE messages SET message_id = "{message_id}" WHERE uuid = "{uuid}"')
            self.sql.execute(f'UPDATE messages SET deep_linked_url = "{deep_linked_url}" WHERE uuid = "{uuid}"')
        self.db.commit()

    def get_user_position(self, user_id):
        self.sql.execute(f"SELECT position from users WHERE user_id = '{user_id}'")
        return self.sql.fetchone()[0]

    def get_file_stat(self, uuid):
        self.sql.execute(
            f"SELECT downloads, uniq_downloads, downloads_with_subscribe, downloads_with_new_subscribe, description FROM files WHERE uuid = '{uuid}'")
        return self.sql.fetchone()

    def delete_channel(self, channel_id):
        self.sql.execute(f"DELETE FROM channels WHERE channel_id = '{channel_id}' ")
        self.db.commit()

    def get_file_id(self, uuid):
        self.sql.execute(f"SELECT file_id FROM files WHERE uuid = '{uuid}'")
        return self.sql.fetchone()

    def add_file_id(self, file_id, uuid, channel_id, channel_url, description):
        self.sql.execute(
            f"INSERT INTO files VALUES  ('{file_id}', '{uuid}', '{channel_id}',' {channel_url}', 0, 0, 0, 0, '{description}')")
        self.db.commit()

    def get_data_from_file(self, uuid, value):
        self.sql.execute(f"SELECT {value} FROM files WHERE uuid = '{uuid}'")
        return self.sql.fetchone()[0]

    def get_channel_url(self, uuid):
        self.sql.execute(f"SELECT channel_url FROM files WHERE uuid = '{uuid}'")
        return self.sql.fetchone()[0]

    def add_channel(self, channel_id, channel_url):
        self.sql.execute(f"INSERT INTO channels VALUES  ('{channel_id}', '{channel_url}')")
        self.db.commit()

    def get_channels(self):
        self.sql.execute(f"SELECT channel_url, channel_id FROM channels")
        return self.sql.fetchall()

    def get_current_channel_id(self, user_id):
        self.sql.execute(f"SELECT current_channel_id FROM users  WHERE user_id = '{user_id}' ")
        return self.sql.fetchone()[0]

    def get_file_channel(self, uuid):
        self.sql.execute(f"SELECT channel_id FROM files WHERE uuid = '{uuid}'")
        return self.sql.fetchone()[0]

    def get_selected_channel_id(self, user_id):
        self.sql.execute(f"SELECT selected_channel_id FROM users  WHERE user_id = '{user_id}' ")
        return self.sql.fetchone()[0]

    def get_channel_url_by_id(self, channel_id):
        self.sql.execute(f"SELECT channel_url FROM channels WHERE channel_id = '{channel_id}'")
        return self.sql.fetchone()[0]

    def increase(self, value, uuid):
        print(value, uuid)
        self.sql.execute(f"UPDATE files SET {value} = {value} + 1 WHERE uuid = '{uuid}' ")
        self.db.commit()

    def debug_info(self):
        self.sql.execute(f"SELECT * from users")
        print(self.sql.fetchall())
