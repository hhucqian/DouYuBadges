# -*- coding: UTF-8 -*-

import sqlite3

class BadgeServer:
    def __init__(self):
        self.conn = sqlite3.connect('data.db', check_same_thread = False)
        self.badge_dict = {}
        self.load_from_db()

    def load_from_db(self):
        c = self.conn.cursor()
        c.execute("select name, room_id from badges")
        for item in c.fetchall():
            self.badge_dict[item[0]] = item[1]
    
    def add_badge(self, name, room_id):
        if name not in self.badge_dict:
            self.badge_dict[name] = room_id
            self.insert_badge_to_db(name, room_id)

    def insert_badge_to_db(self, name, room_id):
        print("get new badge {0}-->{1}".format(name, room_id))
        self.conn.execute("insert into badges(name, room_id) values(?, ?)",(name, room_id))
        self.conn.commit()

    def __str__(self):
        return str(self.badge_dict)
