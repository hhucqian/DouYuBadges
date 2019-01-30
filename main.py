# -*- coding: UTF-8 -*-

from douyuroom import DouyuRoom


def main():
    room = DouyuRoom(99999)
    print(room)
    room.start_job()

if __name__ == '__main__':
    main()
