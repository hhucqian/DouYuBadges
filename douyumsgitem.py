# -*- coding: UTF-8 -*-


class DouyuMsgItem:
    def __init__(self, msg: bytes):
        self.kv_dict = {}
        try:
            msg_content = msg[12:].decode("utf-8", 'ignore').split('/')
            for item in msg_content:
                kv = item.split("@=")
                if len(kv) > 1:
                    self.kv_dict[kv[0]] = kv[1]
        except:
            print("err:", msg)

    def is_chat_msg(self):
        return self.type == "chatmsg"

    def __getattr__(self, name):
        if name in self.kv_dict:
            return self.kv_dict[name]
        return None

    def __str__(self):
        return str(self.kv_dict)
