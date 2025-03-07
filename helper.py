# -*- coding:utf-8 -*-
from __future__ import print_function
import ctypes, sys, time, os, random, json
import keyboard
import cv2
from tqdm import tqdm
from datetime import datetime
import subprocess
from ppadb.client import Client
import tkinter as tk
from tkinter import messagebox
from collections import deque
from logger import Logger

class Helper():

    def __init__(self, num_runs=100, config_file_index = 0, host="127.0.0.1", port=5037, logger=None):
        
        self.notCheck = []
        self.failCount = 0
        self.wait = False # 暂停
        self.logger = logger
        if self.logger is None:
            logger = Logger('app')
            self.logger = logger

        self.connect_to_device(host, port)

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.attributes('-topmost', True)  # 将窗口设置为置顶

        # 通过adb获取设备分辨率
        device_info = self.device.shell("wm size")
        parts = device_info.strip().split(': ')[1].split('x')
        self.device_width = int(parts[0])
        self.device_height = int(parts[1])

        self.queue = deque(maxlen=10)  # 保存最近10次的结果

        self.load_config(config_file_index, num_runs)

        print('按下 F10 停止运行脚本')
        print('按下 F12 暂停/运行脚本')
        print()
        keyboard.on_press_key("F10", self.switchConfig)
        keyboard.on_press_key("F12", self.pause)

    def connect_to_device(self, host, port):
        try:
            # 创建 ADB 客户端
            client = Client(host="127.0.0.1", port=5037)
            # 获取设备列表
            devices = client.devices()
            if len(devices) == 0:
                print("No devices found")
                return
            elif len(devices) == 1:
                self.device = devices[0]
            else:
                print("设备序号：")
                for i, device in enumerate(devices):
                    print(f"[{i}]: {device.serial}")
                print("请选择设备序号：", end="")
                deviceId = input()
                deviceId = int(deviceId) if deviceId != "" else 0
                self.device = devices[deviceId]
            
            print(f"Connected to {self.device.serial}")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect: {e}")

    def load_config(self, config_file_index, num_runs):
        print("选择配置文件")
        for files in os.walk('./configs'):
            for index,file in enumerate(files[2]):
                configName = os.path.splitext(file)[0][7:]
                # 如果以数字开头，去掉数字
                while configName[0].isdigit():
                    configName = configName[1:]
                print('[%d] %s' % (index, configName))
            print()
            print('默认选择 [%d]，请输入：' % config_file_index,end="")
            config_file_input = input()
            config_file = './configs/' + (files[2][int(config_file_input)] if config_file_input != "" else files[2][int(config_file_index)])
            # print(config_file)

            with open(config_file,'r',encoding='utf-8') as file:
                try:
                    config = json.load(file)

                    self.path = config.pop('path')
                    self.endFlag = config.pop('endFlag')
                    self.timeCost = config.pop('timeCost') # 流程最少耗时，单位秒
                    self.failFlag = config.pop('failFlag')
                    if config.get('stopFlag') is not None:
                        self.stopFlags = config.pop('stopFlag')
                    else:
                        self.stopFlags = None
                        
                    if config.get('failNum') is not None:
                        self.failNum = config.pop('failNum')
                    else:
                        self.failNum = 10

                    if config.get('refreshConfig') is not None:
                        self.refreshConfig = config.pop("refreshConfig")
                        self.refreshNum = config.pop("refreshNum")
                    else:
                        self.refreshConfig = None

                    self.progressConfig = config.pop("progressConfig")
                    
                
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误: {e}")
                    self.logger.error(f"JSON 解析错误: {e}")
                    return
                except FileNotFoundError:
                    print(f"文件未找到: {file}")
                    self.logger.error(f"文件未找到: {file}")
                    return
                except Exception as e:
                    print(f"发生其他错误: {e}")
                    self.logger.error(f"发生其他错误: {e}")
                    return

        # Get the input for total running time
        print("运行次数(默认%d)：" % num_runs, end="")
        num_runs_input = input()
        num_runs = int(num_runs_input) if num_runs_input != "" else num_runs

        print()
        print('%s 开始运行 %s' % ('*'*20,'*'*20))
        print()
        print('配置文件：%s' % config_file)
        print('运行次数：%d' % num_runs)
        self.logger.info(f"配置文件：{config_file}")
        self.logger.info(f"运行次数：{num_runs}")

        # Initialize progressing bar with the total running times
        self.pbar = tqdm(total=num_runs, ascii=True)
        self.pbar.n = 0
    
    def __del__(self):
        self.pbar.close()
        self.root.destroy()
        subprocess.run(["adb/adb.exe", "kill-server"], check=True)

    def click(self,x, y):
        # print(f"Clicking at ({x}, {y})")
        self.device.shell(f"input tap {x} {y}")

    def screenshot(self):
        path = os.path.abspath('.') + '\images\\'
        self.device.shell("screencap -p /sdcard/screenshot.png")
        self.device.pull("/sdcard/screenshot.png", f"{path}screenshot.png")
        
    def Image_to_position(self,image, m = 0, similarity = 0.9):
        # cv2.imread 不支持中文路径
        image_path = 'images/' + self.path + str(image) + '.png'
        screen = cv2.imread('images/screenshot.png', 0)
        template = cv2.imread(image_path, 0)

        methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED]
        image_x, image_y = template.shape[:2]
        if screen is None :
            print('screen图片未找到')
            return False
        if template is None:
            print('template图片未找到')
            return False
        result = cv2.matchTemplate(screen, template, methods[m])
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        w, h = template.shape[1], template.shape[0]
        # 对于 cv2.TM_CCORR_NORMED 我们关注最大匹配位置
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        # 绘制矩形框标记匹配区域
        cv2.rectangle(screen, top_left, bottom_right, (0, 255, 0), 2)

        # 显示结果
        # print({'image':image,'max_val':max_val})
        # cv2.imshow('Matched Image', screen)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        if max_val >= similarity:
            global coord
            # center = (max_loc[0] + image_y / 2, max_loc[1] + image_x / 2)
            coord = (max_loc[0], max_loc[1])
            # print(f'image:{image}, similarity:{max_val}, coordinate:{coord}')
            return coord
        else:
            return False
    
    def recursion(self,images):

        for img,cnf in images.items():
            if img in self.notCheck:
                continue

            similarity = cnf.get('similarity') if cnf.get('similarity') is not None else 0.9
            # 查找图片
            if self.Image_to_position(img, m = 0,similarity=similarity) != False:
                # 找到图片看是否点击或继续递归查找
                if cnf.get('found') is not None:
                    # print(f"Found {img}")
                    # 立即点击
                    if type(cnf.get('found')) == int:
                        self.now_img = img
                        # time.sleep(0.2)
                        offsetX = int((cnf.get('offsetX') if cnf.get('offsetX') is not None else 0))
                        offsetY = int((cnf.get('offsetY') if cnf.get('offsetY') is not None else 0))

                        x = int(coord[0]) + random.randrange(int(50)) + offsetX
                        y = int(coord[1]) + random.randrange(int(25)) + offsetY

                        for i in range(cnf.get('found')):
                            self.click(x,y)
                            self.queue.append(self.now_img)
                            time.sleep(cnf.get('delay') if cnf.get('delay') is not None else 0)

                        # 单次流程不再检查
                        if cnf.get('checkAgain') is not None:
                            if cnf.get('checkAgain') == 0:
                                self.notCheck.append(cnf.get('checkImg'))
                    elif cnf.get('found') == 'pass':
                        self.now_img = img
                        return
                    else:
                        self.recursion(cnf['found'])
            else:
                # 找不到图片看是否有操作或继续递归查找
                if cnf.get('notFound') is not None:
                    if cnf.get('notFound') == 'pass':
                        pass
                    else:
                        self.recursion(cnf['notFound'])

    def pause(self,key):
        self.wait = not self.wait
        if self.wait == True:
            print('暂停运行，按 F12 继续运行')
            self.logger.info('暂停运行')
        else:
            print('开始运行，按 F12 暂停运行')
            self.logger.info('开始运行')
    
    def switchConfig(self,key):
        self.wait = False      # 防止按了 F12 又按 F10
        print('停止运行当前脚本，可以继续选择其他配置文件')
        self.logger.info('手动停止运行当前脚本')
        self.pbar.n = self.pbar.total

    def run(self):
        self.now_img = ''
        self.time = datetime.now()
        while True:
            while not self.wait:
                
                if self.pbar.n >= self.pbar.total:
                    self.logger.info('任务完成')
                    return
                
                self.screenshot()

                self.recursion(self.progressConfig)

                # 如果连续10次都是同一个图片，需要执行卡住后的流程
                if len(self.queue) == 10 and len(set(self.queue)) == 1:
                    if self.refreshConfig is not None:
                        print('连续10次都是同一个图片，开始执行卡住后的流程')
                        self.logger.warning('连续10次都是同一个图片，开始执行卡住后的流程')
                        for i in range(self.refreshNum):
                            self.screenshot()
                            self.recursion(self.refreshConfig)
                    
                # 一个完整流程结束，可能多次点击 
                if self.now_img == self.endFlag:
                    # 判断当前时间与上次一次完整流程的时间差  
                    if (datetime.now() - self.time).seconds >= self.timeCost:
                        self.time = datetime.now()
                        self.notCheck = []
                        self.pbar.update()
                        if self.pbar.n >= self.pbar.total:
                            return
                        time.sleep(0.5 + random.random() * 0.02)
                elif self.now_img == self.failFlag:
                    self.failCount += 1
                    self.notCheck = []
                    print('已失败 %d 次！！！' % self.failCount)
                    time.sleep(2 + random.random() * 0.02)
                    if self.failCount%self.failNum == 0:
                        self.wait = True
                        print('暂停运行，按 F12 继续运行')
                        self.logger.warning(f"失败 {self.failCount} 次 ！！！")
                        # messagebox.showwarning("警告", "失败 %d 次 ！！！\n暂停运行，按 F12 继续运行" % self.failCount)
                        result = messagebox.askyesno(
                                    "警告", f"失败 {self.failCount} 次 ！！！\n是否继续运行",
                                    icon='warning',
                                    type=messagebox.YESNO
                                )
                        if result:
                            self.wait = False
                            print('开始运行，按 F12 暂停运行')
                        else:
                            print('停止运行当前任务')
                            return
                if self.stopFlags is not None:
                    for stopImg in self.stopFlags:
                        if self.now_img == stopImg:
                            print('停止运行当前任务')
                            return
        
          

# def is_admin():
#         try:
#             return ctypes.windll.shell32.IsUserAnAdmin()
#         except:
#             return False

# if __name__ == '__main__': 
#     # if is_admin():


#         helper = Helper(config_file_index = 0, host="127.0.0.1", port=5037)
#         helper.run()
#         helper.__del__()
    # else:
    #     if sys.version_info[0] == 3:
    #         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  
   
