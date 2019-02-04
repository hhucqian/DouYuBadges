# -*- coding: UTF-8 -*-

import json
import threading
import time
import urllib.request

from badgeserver import BadgeServer
from douyuroom import DouyuRoom


class SpiderDispatcher:
    def __init__(self):
        self.job_list = []
        self.badge_server = BadgeServer()
        self.room_id_filter = {}

    def load_room_id_list(self):
        with urllib.request.urlopen('http://open.douyucdn.cn/api/RoomApi/live?limit=100') as f:
            content = f.read().decode('utf-8')
            content = json.loads(content)
            if content['error'] != 0:
                return None
            else:
                res = []
                for item in content['data']:
                    res.append((item['room_id'], item['nickname']))
                return res

    def print_record_count(self):
        while True:
            time.sleep(20)
            print('database record count:', self.badge_server.get_record_count(),
                  'current room count:', len(self.job_list))

    def start(self):
        t = threading.Thread(target=self.print_record_count)
        t.setDaemon(True)
        t.start()
        room_id_list = self.load_room_id_list()
        if room_id_list is not None:
            for room_id in room_id_list:
                dy_room = DouyuRoom(room_id[0], room_id[1], self.badge_server)
                t = threading.Thread(target=dy_room.start_job)
                t.setDaemon(True)
                t.start()
                self.job_list.append(dy_room)

        while True:
            time.sleep(5 * 60)
            stamp_level = 0
            jobs_to_stop = [
                job for job in self.job_list if job.record_stamp <= stamp_level or job.is_stop]
            jobs_to_continue = [
                job for job in self.job_list if job.record_stamp > stamp_level]
            running_room_id_list = [
                job.room_id for job in self.job_list if job.record_stamp > stamp_level]
            self.job_list = jobs_to_continue

            for room_id in self.room_id_filter.keys():
                self.room_id_filter[room_id] -= 1
            self.room_id_filter = {
                k: v for (k, v) in self.room_id_filter.items() if v > 0}

            for job in jobs_to_stop:
                job.stop_job()
                self.room_id_filter[job.room_id] = 10

            room_id_list = self.load_room_id_list()
            for room_id in room_id_list:
                if room_id[0] not in running_room_id_list:
                    if room_id[0] in self.room_id_filter.keys():
                        self.room_id_filter[room_id[0]] -= 1
                    else:
                        dy_room = DouyuRoom(
                            room_id[0], room_id[1], self.badge_server)
                        t = threading.Thread(target=dy_room.start_job)
                        t.setDaemon(True)
                        t.start()
                        self.job_list.append(dy_room)

            print('room list:', ' '.join(
                [job.nickname for job in self.job_list]))
