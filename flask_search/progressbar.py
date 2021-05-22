from tkinter import *
from tkinter import ttk


class GressBar:

    def start(self):
        top = Toplevel()  # 弹出式窗口，实现多窗口时经常用到
        self.master = top
        top.overrideredirect(True)  # 去除窗体的边框
        top.title("进度条")
        Label(top, text="正在扫描选定路径的文件,请稍等……", fg="blue").pack(pady=2)
        prog = ttk.Progressbar(top, mode='indeterminate', length=200)  # 创建进度条
        prog.pack(pady=10, padx=35)
        prog.start()

        top.resizable(False, False)  # 参数为false表示不允许改变窗口尺寸
        top.update()
        # 计算窗口大小，使显示在屏幕中央
        curWidth = top.winfo_width()
        curHeight = top.winfo_height()
        scnWidth, scnHeight = top.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        top.geometry(tmpcnf)
        top.mainloop()

    def quit(self):
        if self.master:
            self.master.destroy()