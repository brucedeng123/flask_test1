import sqlite3


class DataMgr:

    def __init__(self):
        # 创建或打开一个数据库
        # check_same_thread 属性用来规避多线程操作数据库的问题
        self.conn = sqlite3.connect("file.db", check_same_thread=False)
        # 建表
        self.conn.execute('create table if not exists disk_table(' 
                          'id integer primary key autoincrement,' 
                          'file_path text,' 
                          'drive_letter text)')
        # 创建索引 用来提高搜索速度
        self.conn.execute('create index if not exists index_path on disk_table(file_path)')

    # 批量插入数据
    def batch_insert(self, data):
        for line in data:
            self.conn.execute('insert into disk_table values (null,?,?)', line)
        self.conn.commit()

    # 模糊搜索
    def query(self, key):
        cursor = self.conn.cursor()
        cursor.execute("select file_path from disk_table where file_path like ?", ('%{0}%'.format(key),))
        r = [row[0] for row in cursor]
        cursor.close()
        return r

    def close(self):
        self.conn.close()