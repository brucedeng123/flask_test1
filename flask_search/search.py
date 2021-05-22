from tkinter import *
from tkinter import ttk
import tkinter.filedialog as dir
import queue
import threading
import progressbar
import disk
from datebase import DataMgr


class SearchUI:

    def __init__(self):
        # 创建一个消息队列
        self.notify_queue = queue.Queue()
        root = Tk()
        self.master = root
        self.create_menu(root)
        self.create_content(root)
        self.path = 'D:'
        root.title('the search tool')
        root.update()
        # 在屏幕中心显示窗体
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        scnWidth, scnHeight = root.maxsize()  # 得到屏幕的宽度和高度
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth)/2, (scnHeight-curHeight)/2)
        root.geometry(tmpcnf)

        # 创建一个进度条对话框实例
        self.gress_bar = progressbar.GressBar()

        # 创建一个数据库的实例
        self.data_mgr = DataMgr()

        # 在UI线程启动消息队列循环
        self.process_msg()
        root.mainloop()

    # ui线程与扫描线程同步
    def process_msg(self):
        # after方法，相当于一个定时器，
        # 第一个参数是时间的毫秒值，
        # 第二个参数指定执行一个函数
        self.master.after(400, self.process_msg)
        # 这样我们就在主线程建立了一个消息队列，
        # 每隔一段时间去消息队列里看看，
        # 有没有什么消息是需要主线程去做的，
        # 有一点需要特别注意，
        # 主线程消息队列里也不要干耗时操作，
        # 该队列仅仅用来更新UI。
        while not self.notify_queue.empty():
            try:
                msg = self.notify_queue.get()
                if msg[0] == 1:
                    self.gress_bar.quit()

            except queue.Empty:
                pass

    # 扫描线程工作
    def execute_asyn(self):
        # 定义一个scan函数，放入线程中去执行耗时扫描
        def scan(_queue):
            if self.path:
                paths = disk.scan_file(self.path)  # 位于disk.py
                self.data_mgr.batch_insert(paths)  # 位于database.py

            _queue.put((1,))
        th = threading.Thread(target=scan, args=(self.notify_queue,))
        th.setDaemon(True)  # 设置为守护进程
        th.start()

        self.gress_bar.start()

    # 菜单绘制
    def create_menu(self, root):
        menu = Menu(root)  # 创建菜单

        # 二级菜单
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label='设置路径', command=self.open_dir)
        file_menu.add_separator()
        file_menu.add_command(label='扫描', command=self.execute_asyn)

        about_menu = Menu(menu, tearoff=0)
        about_menu.add_command(label='version1.0')

        # 在菜单栏中添加菜单
        menu.add_cascade(label='文件', menu=file_menu)
        menu.add_cascade(label='关于', menu=about_menu)
        root['menu'] = menu

    # 主界面绘制
    def create_content(self, root):
        lf = ttk.LabelFrame(root, text='文件搜索')
        lf.pack(fill=X, padx=15, pady=8)

        top_frame = Frame(lf)
        top_frame.pack(fill=X, expand=YES, side=TOP, padx=15, pady=8)

        self.search_key = StringVar()
        ttk.Entry(top_frame, textvariable=self.search_key, width=50).pack(fill=X, expand=YES, side=LEFT)
        ttk.Button(top_frame, text="搜索", command=self.search_file).pack(padx=15, fill=X, expand=YES)

        bottom_frame = Frame(lf)
        bottom_frame.pack(fill=BOTH, expand=YES, side=TOP, padx=15, pady=8)

        band = Frame(bottom_frame)
        band.pack(fill=BOTH, expand=YES, side=TOP)

        self.list_val = StringVar()
        listbox = Listbox(band, listvariable=self.list_val, height=18)
        listbox.pack(side=LEFT, fill=X, expand=YES)

        vertical_bar = ttk.Scrollbar(band, orient=VERTICAL, command=listbox.yview)
        vertical_bar.pack(side=RIGHT, fill=Y)
        listbox['yscrollcommand'] = vertical_bar.set

        horizontal_bar = ttk.Scrollbar(bottom_frame, orient=HORIZONTAL, command=listbox.xview)
        horizontal_bar.pack(side=BOTTOM, fill=X)
        listbox['xscrollcommand'] = horizontal_bar.set

        # 给list动态设置数据，set方法传入一个元组
        self.list_val.set(('等待搜索',))

    # 搜索文件
    def search_file(self):
        if self.search_key.get():
            result_data = self.data_mgr.query(self.search_key.get())
            if result_data:
                 self.list_val.set(tuple(result_data))

    # 指定文件夹
    def open_dir(self):
        d = dir.Directory()
        self.path = d.show(initialdir=self.path)


if __name__ == '__main__':
    SearchUI()