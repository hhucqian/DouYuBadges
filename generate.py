# -*- coding: UTF-8 -*-

import sqlite3


def main():
    conn = sqlite3.connect("data.db")
    c = conn.execute("select name , room_id from badges order by name")
    item_line = []
    records = c.fetchall()
    for item in records:
        item_line.append(
            "[{0}](http://www.douyu.com/{1})".format(item[0], item[1]))
    with open("docs/README.md", "w", encoding="utf-8") as f:
        f.write("# 斗鱼粉丝牌不完全大全（持续更新中）\n\n")
        f.write("## 当前收录粉丝牌总数{0} \n\n".format(len(records)))
        f.write("|1  |2  |3  |4  |5  |\n")
        f.write("|---|---|---|---|---|\n")
        item_count = len(item_line)
        for index in range(item_count):
            f.write("| {0} ".format(item_line[index]))
            if index % 5 == 4 or index == item_count - 1:
                f.write("|\n")


if __name__ == '__main__':
    main()
