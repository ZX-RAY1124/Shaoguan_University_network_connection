import time
import threading
from datetime import datetime, timedelta
import os
from tkinter import messagebox
import wang as net

class Scheduler:
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        self.file_modified_time = 0  # 记录文件最后修改时间
        self.reload_event = threading.Event()  # 重新加载事件
        
    def read_times_from_file(self, filename='list.txt'):
        """从文件中读取时间列表"""
        times = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # 跳过空行和注释
                        parts = line.split(':')
                        if len(parts) >= 2:  # 至少有小时和分钟
                            try:
                                hour = int(parts[0])
                                minute = int(parts[1])
                                second = int(parts[2]) if len(parts) > 2 else 0
                                times.append((hour, minute, second))
                            except ValueError:
                                print(f"警告：跳过无效的时间格式: {line}")
        except FileNotFoundError:
            print(f"错误：找不到文件 {filename}")
        
        return times
    
    def get_next_run_time(self, target_times):
        """获取下一个运行时间"""
        now = datetime.now()
        current_time = now.time()
        
        # 先尝试当天的时间
        for hour, minute, second in target_times:
            target_time = datetime.combine(now.date(), datetime.min.time()).replace(hour=hour, minute=minute, second=second).time()
            if target_time > current_time:
                # 如果目标时间在今天还未到达，则返回今天的时间
                return datetime.combine(now.date(), target_time)
        
        # 如果今天的所有时间都已过去，则返回明天的第一个时间
        if target_times:
            hour, minute, second = target_times[0]  # 使用第一个时间
            tomorrow = now + timedelta(days=1)
            return datetime.combine(tomorrow.date(), datetime.min.time()).replace(hour=hour, minute=minute, second=second)
        
        return None
    
    def auto_login(self):
        """执行自动登录，使用与Main.py中相同的逻辑"""
        try:
            # 从配置文件读取用户名和密码，模仿Main.py中的逻辑
            with open('properties.prop', 'r', encoding='utf-8') as f:
                identify = f.readlines()
                ans = []
                for line in identify:
                    stripped_line = line.strip('\n').strip()
                    if stripped_line and '=' in stripped_line:
                        ans.append(stripped_line.split("=", 1))
            
            # 提取用户名和密码
            username = None
            password = None
            for item in ans:
                if item[0] == 'name':
                    username = item[1]
                elif item[0] == 'password':
                    password = item[1]
            
            if username is None or password is None:
                self._show_message("定时登录", "配置文件中缺少用户名或密码", "error")
                return False
            
            # 执行登录，模仿Main.py中的逻辑
            suc = net.login(username, password)
            
            if suc == False:
                self._show_message("定时登录", "校园网已登录", "error")
                return False
            else:
                self._show_message("定时登录", "登录成功", "info")
                return True
                
        except Exception as e:
            self._show_message("定时登录", f"自动登录过程出错: {e}", "error")
            return False

    def _show_message(self, title, msg, msg_type):
        """在GUI线程中显示弹窗"""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            if msg_type == "info":
                messagebox.showinfo(title, msg)
            elif msg_type == "warning":
                messagebox.showwarning(title, msg)
            else:
                messagebox.showerror(title, msg)
            root.destroy()
        except Exception:
            pass
    
    def check_file_changed(self):
        """检查list.txt文件是否被修改"""
        try:
            current_modified_time = os.path.getmtime('list.txt')
            if current_modified_time > self.file_modified_time:
                self.file_modified_time = current_modified_time
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检测到list.txt文件已更改，将重新加载时间配置")
                self.reload_event.set()  # 设置重新加载事件
                return True
        except FileNotFoundError:
            pass
        return False
    
    def scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            try:
                # 检查文件是否被修改
                self.check_file_changed()
                
                # 读取时间列表
                target_times = self.read_times_from_file()
                
                if not target_times:
                    print("没有找到有效的时间配置，等待1分钟后重试...")
                    time.sleep(60)
                    continue
                
                # 获取下一个运行时间
                next_run_time = self.get_next_run_time(target_times)
                
                if next_run_time:
                    # 计算等待时间
                    wait_seconds = (next_run_time - datetime.now()).total_seconds()
                    
                    if wait_seconds <= 0:
                        # 如果计算出的时间差小于等于0，说明时间已过，重新计算
                        time.sleep(1)
                        continue
                    
                    print(f"下次自动登录时间: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}，等待 {int(wait_seconds)} 秒...")
                    
                    # 等待到下一个时间点，期间检查文件更改和停止信号
                    slept = 0
                    
                    while slept < wait_seconds and self.running:
                        # 检查文件是否被修改
                        if self.check_file_changed():
                            print("检测到配置更改，重新计算登录时间...")
                            break  # 跳出循环，重新读取配置
                        
                        sleep_time = min(1, wait_seconds - slept)
                        time.sleep(sleep_time)
                        slept += sleep_time
                        
                        # 检查当前时间是否达到目标时间
                        now = datetime.now()
                        for hour, minute, second in target_times:
                            current_time = now.time()
                            target_time = datetime.combine(now.date(), datetime.min.time()).replace(hour=hour, minute=minute, second=second).time()
                            
                            # 如果当前时间匹配目标时间（允许1秒的误差）
                            if target_time <= current_time <= target_time.replace(second=target_time.second + 1):
                                self.auto_login()
                                time.sleep(1)  # 避免重复触发
                                break
                else:
                    print("无法计算下一个运行时间，等待1分钟后重试...")
                    time.sleep(60)
            except Exception as e:
                print(f"调度器运行出错: {e}，等待1分钟后重试...")
                time.sleep(60)
        
        print("调度器已停止")
    
    def start(self):
        """启动调度器"""
        if not self.running:
            self.running = True
            # 记录初始文件修改时间
            try:
                self.file_modified_time = os.path.getmtime('list.txt')
            except FileNotFoundError:
                pass
            self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            print("定时登录调度器已启动")
        
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)  # 等待最多2秒让线程结束
        print("定时登录调度器已停止")


def main():
    scheduler = Scheduler()
    try:
        scheduler.start()
        print("调度器已启动，按 Ctrl+C 停止")
        while True:
            time.sleep(1)  # 主线程持续运行
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止调度器...")
        scheduler.stop()

if __name__ == "__main__":
    main()