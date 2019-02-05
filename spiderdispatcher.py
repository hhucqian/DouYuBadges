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

    def load_room_info_list(self):
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
        room_info_list = self.load_room_info_list()
        if room_info_list is not None:
            for room_info in room_info_list:
                dy_room = DouyuRoom(room_info[0], room_info[1], self.badge_server)
                t = threading.Thread(target=dy_room.start_job)
                t.setDaemon(True)
                t.start()
                self.job_list.append(dy_room)

        while True:
            time.sleep(5 * 60)
            stamp_level = 0
            jobs_to_stop = [
                job for job in self.job_list if job.record_stamp <= stamp_level or job.is_stop]
            room_info_list = self.load_room_info_list()
            room_id_to_run_list = [item[0] for item in room_info_list]

            for job in jobs_to_stop:
                if job.room_id not in room_id_to_run_list:
                    job.stop_job()
                    self.job_list.remove(job)

            running_room_id_list = [item.room_id for item in self.job_list]

            for room_info in room_info_list:
                if room_info[0] not in running_room_id_list:
                    dy_room = DouyuRoom(
                        room_info[0], room_info[1], self.badge_server)
                    t = threading.Thread(target=dy_room.start_job)
                    t.setDaemon(True)
                    t.start()
                    self.job_list.append(dy_room)

            for job in self.job_list:
                job.record_stamp = 0
