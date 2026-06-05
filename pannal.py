import tkinter
from tkinter import messagebox
import queue

class pannal:
    def __init__(self):
        self.GUI = tkinter.Tk()
        self.GUI.title("这是校园网连接系统")
        self.center_window(self.GUI, 400, 260)
        # 设置窗口关闭协议
        self.GUI.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.tips = tkinter.LabelFrame(self.GUI, text="请输入时间")
        self.tips_h = tkinter.Label(self.tips, text="小时")
        self.tips_m = tkinter.Label(self.tips, text="分钟")
        self.tips_s = tkinter.Label(self.tips, text="秒")
        self.name = tkinter.Label(self.GUI, text="时间列表")

        self.hour = tkinter.Entry(self.tips, width=2)
        self.minute = tkinter.Entry(self.tips, width=2)
        self.secund = tkinter.Entry(self.tips, width=2)
        self.divider = tkinter.Label(self.tips, text=":")
        self.divider_1 = tkinter.Label(self.tips, text=":")
        self.listbox = tkinter.Listbox(self.GUI, width=10, height=10)

        self.sure = tkinter.Button(self.GUI, text="确定", width=15, height=1, command=self.on_sure_press)
        self.del_ = tkinter.Button(self.GUI, text="清除", width=15, height=1, command=self.clear)
        self.insert = tkinter.Button(self.GUI, text="插入", width=15, height=1, command=self.insert)
        self.del_list = tkinter.Button(self.GUI, text="删除选中项", width=15, height=1, command=self.del_listbox)
        self.save = tkinter.Button(self.GUI, text="保存配置", width=15, height=1, command=self.save_)
        self.del_all = tkinter.Button(self.GUI, text="清空列表", width=15, height=1, command=self.clear_all)

        self.tips.grid(column=0, row=0)
        self.tips_h.grid(column=0, row=0)
        self.tips_m.grid(column=2, row=0)
        self.tips_s.grid(column=4, row=0)
        self.name.grid(column=1, row=0)

        self.hour.grid(column=0, row=1, padx=0.5)
        self.minute.grid(column=2, row=1, padx=0.5)
        self.secund.grid(column=4, row=1, padx=0.5)

        self. divider_1.grid(column=1, row=1)
        self.divider.grid(column=3, row=1)

        self.sure.grid(column=0, row=1)

        self.del_.grid(column=0, row=2)
        self.insert.grid(column=0, row=3)
        self.del_list.grid(column=0, row=4)
        self.save.grid(column=0, row=5)
        self.del_all.grid(column=2, row=1)

        self.listbox.grid(column=1, row=1, rowspan=5)

        self.get_list()

    def center_window(self,root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def on_sure_press(self):
        if not self.hour.get() or not self.minute.get() or not self.secund.get():
            return
        else:
            res = '%s:%s:%s' % (self.hour.get(), self.minute.get(),self.secund.get())
            if self.listbox.get(0):
                for i in self.listbox.get(0, tkinter.END):
                    if i == res:
                        return

                self.listbox.insert(tkinter.END, res)

            else:
                self.listbox.insert(tkinter.END, res)
        return

    def clear(self):
        self.hour.delete(0, tkinter.END)
        self.minute.delete(0, tkinter.END)
        self.secund.delete(0, tkinter.END)

    def insert(self):
        selected = self.listbox.curselection()
        if not selected and (not self.hour.get() or not self.minute.get() or not self.secund.get()):
            return
        else:
            if selected:
                res = '%s:%s:%s' % (self.hour.get(), self.minute.get(), self.secund.get())
                self.listbox.insert(selected, res)
                return
            else:
                return

    def del_listbox(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        else:
            self.listbox.delete(selected)
            return

    def get_list(self):
        try:
            file = open('list.txt', mode='r')
            i = 0
            for line in file.readlines():
                self.listbox.insert(i, line.strip())
                i+=1
            file.close()
        except Exception as e:
            print(e)
        finally:
            return

    def save_(self):
        try:
            file = open('list.txt', mode='w')
            for line in self.listbox.get(0,tkinter.END):
                time_str = line.strip()
                if time_str:
                    file.write(time_str + '\n')
            file.close()
        except Exception as e:
            print(e)
        finally:
            self.GUI.after(0, lambda: messagebox.showinfo("信息","保存成功"))
            return

    def clear_all(self):
        self.listbox.delete(0,tkinter.END)


    def start(self):
        self.GUI.mainloop()
    
    def on_closing(self):
        # 当用户点击窗口关闭按钮时销毁窗口
        self.GUI.destroy()