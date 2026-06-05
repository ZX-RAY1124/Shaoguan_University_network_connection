import os.path
import os
import threading
import winreg
import sys
from tkinter import messagebox

import pystray
from PIL import Image


import pannal
import wang as net
import config
import scheduler



def make_sub():
    icon = Image.open("icon.png").resize((32,32))
    menu = pystray.Menu(
        pystray.MenuItem('检测状态',lambda:check()),
        pystray.MenuItem('设置开机自启动(根据配置文件)',lambda: autorun()),
        pystray.MenuItem('上线',lambda: main()),
        pystray.MenuItem('下线',lambda: logout()),
        pystray.MenuItem('配置程序',lambda: threading.Thread(target=lambda: conf(), daemon=True).start()),
        #pystray.MenuItem('打开配置文件', lambda: os.startfile('properties.prop')),
        pystray.MenuItem('创建计时任务', lambda : threading.Thread(target=lambda : make_time_process(), daemon=True).start()),
        pystray.MenuItem('退出程序', lambda: sub.stop())
    )
    sub = pystray.Icon('sub_level', icon, menu=menu)

    sub.run_detached()

def check():
    def check_thread():
        try:
            state = net.check_online()
            # 延迟执行GUI更新
            import time
            time.sleep(0.1)  # 短暂延迟以确保pystray菜单已释放
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏根窗口
            if state == True:
                messagebox.showinfo("状态", "已上线")
            elif state == False:
                messagebox.showinfo("状态", "未上线")
            else:
                messagebox.showwarning("错误", "无法确认校园网状态,请检查网络连接")
            root.destroy()
        except Exception as e:
            # 延迟执行GUI更新
            import time
            time.sleep(0.1)  # 短暂延迟以确保pystray菜单已释放
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏根窗口
            messagebox.showerror("提示", f"检测状态时出错: {e}")
            root.destroy()
    
    # 启动新线程执行检测操作
    threading.Thread(target=check_thread, daemon=True).start()



def make_time_process():
    tk =  pannal.pannal()
    tk.start()

def conf():
    # 使用with语句确保资源正确释放
    tkc = config.config()
    tkc.start()

def autorun():
    try:
        f = open(get_file_dir("properties.prop"), "r", encoding="utf-8")
        identify = f.readlines()
        ans = []
        for line in identify:
            # 跳过注释行和空行
            stripped_line = line.strip('\n').strip()
            if stripped_line and not stripped_line.startswith('#') and '=' in stripped_line:
                ans.append(stripped_line.split("=", 1))  # 使用1作为分割限制，避免因值中包含=号而出错
        dir_app = get_file_dir('make_connection.exe')

        # 寻找power_on_start的值
        power_on_start_value = None
        for item in ans:
            if item[0] == 'power_on_start':
                power_on_start_value = item[1]
                break
        
        # 如果找到了power_on_start值，判断是否需要开机自启动
        if power_on_start_value == 'true':
            if registry_method('r'):
                pass
            else:
                registry_method('w',dir_app)
        else:
            if registry_method('r'):
                registry_method('d')
            else:
                pass
        print(dir_app)
    except Exception as e:
        # 在主线程中显示错误消息
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏根窗口
        messagebox.showerror("提示", f"读取配置文件出错: {e}")
        root.destroy()
        return
    


def main():
    def login_thread():
        try:
            f = open(get_file_dir("properties.prop"), "r", encoding="utf-8")
            identify = f.readlines()
            ans = []
            for line in identify:
                # 跳过注释行和空行
                stripped_line = line.strip('\n').strip()
                if stripped_line and not stripped_line.startswith('#') and '=' in stripped_line:
                    ans.append(stripped_line.split("=", 1))  # 使用1作为分割限制，避免因值中包含=号而出错
            dir_app = get_file_dir('make_connection.exe')
            print(dir_app)
        except Exception as e:
            # 延迟执行GUI更新
            import time
            time.sleep(0.1)  # 短暂延迟以确保pystray菜单已释放
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏根窗口
            messagebox.showerror("提示", f"读取配置文件出错: {e}")
            root.destroy()
            return
        
        # 提取用户名和密码
        username = None
        password = None
        
        for item in ans:
            if item[0] == 'name':
                username = item[1]
            elif item[0] == 'password':
                password = item[1]
        
        if username is None or password is None:
            import time
            time.sleep(0.1)
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("提示", "配置文件中缺少用户名或密码")
            root.destroy()
            return
        
        try:
            suc = net.login(username, password)
            # 延迟执行GUI更新
            import time
            time.sleep(0.1)  # 短暂延迟以确保pystray菜单已释放
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏根窗口
            if suc == False:
                messagebox.showerror("提示", "校园网已登录")
            else:
                messagebox.showinfo("提示", "登录成功")
            root.destroy()
        except Exception as e:
            # 延迟执行GUI更新
            import time
            time.sleep(0.1)  # 短暂延迟以确保pystray菜单已释放
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏根窗口
            messagebox.showerror("提示", f"登录过程出错: {e}")
            root.destroy()

    # 启动新线程执行登录操作
    threading.Thread(target=login_thread, daemon=True).start()
    

def logout():
    def logout_thread():
        try:
            suc = net.logout()
            # 延迟执行GUI更新
            import time
            time.sleep(0.1)  # 短暂延迟以确保pystray菜单已释放
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏根窗口
            if suc == False:
                messagebox.showerror("提示", "校园网未登录")
            else:
                messagebox.showinfo("提示", "下线成功")
            root.destroy()
        except Exception as e:
            # 延迟执行GUI更新
            import time
            time.sleep(0.1)  # 短暂延迟以确保pystray菜单已释放
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # 隐藏根窗口
            messagebox.showerror("提示", f"下线过程出错: {e}")
            root.destroy()

    # 启动新线程执行登出操作
    threading.Thread(target=logout_thread, daemon=True).start()


#开机启动/关闭开机启动
def registry_method(status,dir = ""):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Run',0,winreg.KEY_SET_VALUE)
    if status == 'r':
        try:
            key_r = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0)
            value, regtype = winreg.QueryValueEx(key_r, 'Campus_network_connection')
            if value:
                winreg.CloseKey(key_r)
                return True
            else:
                winreg.CloseKey(key_r)
                return False
        except:
            return False

    if status == 'w':
        winreg.SetValueEx(key,"Campus_network_connection",0,winreg.REG_SZ, dir)
        winreg.CloseKey(key)
        return True
    if status == 'd':
        winreg.DeleteValue(key, "Campus_network_connection")
        return True
    else:
        return False


#获取文件目录
def get_file_dir(file=''):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable),file)
    else:
        try:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)),file)
        except:
            return os.path.join(os.getcwd(),file)



# 全局scheduler实例
global_scheduler = None

def start_scheduler():
    """启动定时登录调度器"""
    global global_scheduler
    global_scheduler = scheduler.Scheduler()
    global_scheduler.start()

def stop_scheduler():
    """停止定时登录调度器"""
    global global_scheduler
    if global_scheduler:
        global_scheduler.stop()

if __name__ == '__main__':
    make_sub()
    autorun()
    # 启动定时登录调度器
    start_scheduler()