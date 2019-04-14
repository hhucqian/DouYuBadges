# -*- coding: UTF-8 -*-

import sqlite3
import threading


class BadgeServer:
    def __init__(self):
        self.conn = sqlite3.connect('data.db', check_same_thread=False)
        self.badge_room_id_set = {}
        self.load_from_db()
        self.lock = threading.Lock()

    def load_from_db(self):
        c = self.conn.cursor()
        c.execute("select name, room_id from badges")
        for item in c.fetchall():
            self.badge_room_id_set[item[1]] = item[0]

    def add_badge(self, name, room_id):
        room_id = int(room_id)
        with self.lock:
            if room_id not in self.badge_room_id_set:
                self.badge_room_id_set[room_id] = name
                self.insert_badge_to_db(name, room_id)
                return True
            elif name != self.badge_room_id_set[room_id]:
                self.badge_room_id_set[room_id] = name
                self.update_badge_to_db(name, room_id)
                return False
            return False

    def insert_badge_to_db(self, name, room_id):
        print("get new badge {0}-->{1}".format(name, room_id))
        self.conn.execute(
            "insert into badges(name, room_id) values(?, ?)", (name, room_id))
        self.conn.commit()

    def update_badge_to_db(self, name, room_id):
        print("update badge {0}-->{1}".format(name, room_id))
        self.conn.execute(
            "update badges set name = ? where room_id = ?", (name, room_id))
        self.conn.commit()

    def get_record_count(self):
        with self.lock:
            c = self.conn.execute("select count(name) from badges;")
            return c.fetchone()[0]
