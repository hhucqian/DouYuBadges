# -*- coding: UTF-8 -*-

import socket
import struct
import threading
import time

from douyumsgitem import DouyuMsgItem
from badgeserver import BadgeServer


class DouyuRoom:
    def __init__(self, room_id, nickname, badge_server):
        self.room_id = room_id
        self.nickname = nickname
        self.send_lock = threading.Lock()
        self.badge_server = badge_server
        self.is_stop = False
        self.record_stamp = 0
        self.t1 = None

    def connect(self):
        host = socket.gethostbyname("openbarrage.douyutv.com")
        port = 8601
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.s.settimeout(1)

    def send_msg(self, msg):
        if self.is_stop:
            return
        data_length = len(msg) + 8
        code = 689
        msgHead = struct.pack('<i', data_length) \
            + struct.pack('<i', data_length) \
            + struct.pack('<h', code) \
            + struct.pack('c', b'\0') + struct.pack('c', b'\0')
        with self.send_lock:
            try:
                self.s.send(msgHead)
                sent = 0
                while sent < len(msg):
                    tn = self.s.send(msg[sent:])
                    sent = sent + tn
            except:
                return

    def login(self):
        login = 'type@=loginreq/roomid@={0}/\0'.format(self.room_id)
        login = login.encode('utf-8')
        self.send_msg(login)

    def join_group(self):
        joingroup = 'type@=joingroup/rid@={0}/gid@=-9999/\0'.format(
            self.room_id)
        joingroup = joingroup.encode('utf-8')
        self.send_msg(joingroup)

    def send_tick(self):
        while True:
            if self.is_stop:
                break
            msg = 'type@=mrkl/\0'
            msg = msg.encode('utf-8')
            self.send_msg(msg)
            time.sleep(45)

    def process_msg(self, msg: bytes):
        msg_item = DouyuMsgItem(msg)
        if msg_item.is_chat_msg() or msg_item.is_dgb_msg():
            if len(msg_item.bnn) > 0:
                if self.badge_server.add_badge(msg_item.bnn, msg_item.brid):
                    self.record_stamp += 1

    def recv_loop(self):
        content = bytes()
        while True:
            try:
                content += self.s.recv(1024)
                index = content.find(b'\0', 12)
                while index > 0:
                    self.process_msg(content[0:index])
                    content = content[index + 1:]
                    index = content.find(b'\0', 12)
            except socket.timeout:
                continue
            except:
                self.s.close()
                self.connect()
                self.login()
                self.join_group()
                content = bytes()
            finally:
                if self.is_stop:
                    break
        self.s.close()

    def start_job(self):
        try:
            self.connect()
            self.login()
            self.join_group()
            t1 = threading.Thread(target=self.send_tick)
            t1.setDaemon(True)
            t1.start()
            self.recv_loop()
        except:
            self.stop_job()

    def stop_job(self):
        self.is_stop = True

    def __str__(self):
        return "DanmuRoom[id={0},nickname={1}]".format(self.room_id, self.nickname)
