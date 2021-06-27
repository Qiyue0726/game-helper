# -*- coding:utf-8 -*-
from __future__ import print_function
import ctypes, sys, time, os, random, json
import keyboard
import cv2
from cv2 import data
import win32gui,win32ui,win32api,win32con
from tqdm import tqdm
from datetime import datetime
# from eprogress import LineProgress, MultiProgressManager


class Helper():

    def __init__(self,title_name='阴阳师-网易游戏',num_runs=100,config_file_index = 0,
                device_width = 2560,device_height= 1440):

        self.title_name = title_name
        self.num_runs = num_runs
        self.device_width = device_width
        self.device_height = device_height
        self.pbars = []
        self.play_nums = {}
        self.times = {}
        self.now_imgs = {}
        self.notChecks = {}
        self.failNum = 0
        self.wait = False # 暂停
        self.handles = []
        self.widths = []
        self.heights = []
        self.handleDCs = []
        self.mfcDCs = []
        self.saveDCs = []
        self.saveBitMaps = []
        self.main_handle_index = 0

        while True:
            if not len(self.handles):
                handle = win32gui.FindWindowEx(None, None, None, self.title_name)
                if handle == 0:
                    print('未找到应用（%s）请先启动应用程序' % self.title_name)
                else:
                    self.handles.append(handle)
            else:
                handle = win32gui.FindWindowEx(None, self.handles[len(self.handles) - 1], None, self.title_name) 
                if handle == 0:
                    break
                else:
                    self.handles.append(handle)

        
        for index,handle in enumerate(self.handles):
            # 设置窗口标题
            # win32gui.SetWindowText(handle, self.title_name + ' - ' + str(index + 1))
            #获取句柄窗口的大小信息
            left, top, right, bot = win32gui.GetWindowRect(handle)
            width = right - left
            height = bot - top
            # print(width,height)
            #返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
            handleDC = win32gui.GetWindowDC(handle)
            #创建设备描述表
            mfcDC = win32ui.CreateDCFromHandle(handleDC)
            #创建内存设备描述表
            saveDC = mfcDC.CreateCompatibleDC()
            #创建位图对象准备保存图片
            saveBitMap = win32ui.CreateBitmap()
            #为bitmap开辟存储空间
            saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)

            self.widths.append(width)
            self.heights.append(height)
            self.handleDCs.append(handleDC)
            self.mfcDCs.append(mfcDC)
            self.saveDCs.append(saveDC)
            self.saveBitMaps.append(saveBitMap)
        
        if len(self.handles) > 1:
            print('请选择需要设置为队长/开车的窗口索引（左上角标题序号）')
            print('默认选择 [1]，请输入：', end="")
            self.main_handle_index = input()


        # 选择配置文件并解析
        print("选择配置文件")
        for files in os.walk('./configs'):
            for index,file in enumerate(files[2]):
                print('[%d] %s' % (index,os.path.splitext(file)[0][7:]))
            print()
            print('默认选择 [%d]，请输入：' % config_file_index,end="")
            config_file_input = input()
            config_file = './configs/' + (files[2][int(config_file_input)] if config_file_input != "" else files[2][int(config_file_index)])
            # print(config_file)

            with open(config_file,'r') as f:
                config = json.load(f)
                self.path = config.pop('path')
                self.endFlag = config.pop('endFlag')
                self.timeCost = config.pop('timeCost') # 流程最少耗时，单位秒
                self.failFlag = config.pop('failFlag')
                self.images = config


        # Get the input for total running time
        print("每个窗口运行次数(默认%d)：" % self.num_runs, end="")
        num_runs_input = input()
        self.num_runs = int(num_runs_input) if num_runs_input != "" else self.num_runs

        print()
        print('%s 开始运行 %s' % ('*'*20,'*'*20))
        print()
        print('配置文件：%s' % config_file)
        print('每个窗口运行次数：%d' % num_runs)
        print('按下 F12 暂停/运行脚本')
        print()

        # self.progress_manager = MultiProgressManager()
        # Initialize progressing bar with the total running times
        for index,handle in enumerate(self.handles):
            # self.progress_manager.put(str(index), LineProgress(total=self.num_runs, title=self.title_name + "-%d" % (index+1), width=50))
            self.pbars.append(tqdm(total=num_runs, ascii=True, desc=self.title_name + "-%d" % (index+1),position=0))
            self.play_nums[index] = 0
            self.times[index] = datetime.now()
            self.now_imgs[index] = ""
            self.notChecks[index] = []
            # self.progress_manager.update(str(index),0)


        keyboard.on_press_key("F12", self.pause)
        keyboard.on_press_key("ESC", self.__del__)
    
    def __del__(self):
        for index,handle in enumerate(self.handles):
            self.pbars[index].close()
            win32gui.SetWindowText(handle,'self.title_name')
            # Remove DCs
            win32gui.DeleteObject(self.saveBitMaps[index].GetHandle())
            self.saveDCs[index].DeleteDC()
            self.mfcDCs[index].DeleteDC()
            win32gui.ReleaseDC(handle, self.handleDCs[index])


    def click(self,x, y, handle_index):
        # print('click %d' % handle_index)
        long_position = win32api.MAKELONG(x,y)

        win32api.SendMessage(self.handles[handle_index], win32con.WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
        time.sleep(0.01 + random.random() * 0.02)
        win32api.SendMessage(self.handles[handle_index], win32con.WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起


    def screenshot(self, handle_index):
        path = os.path.abspath('.') + '\images\\'

        #将截图保存到saveBitMap中
        self.saveDCs[handle_index].SelectObject(self.saveBitMaps[handle_index])
        #保存bitmap到内存设备描述表
        self.saveDCs[handle_index].BitBlt((0,0), (self.widths[handle_index],self.heights[handle_index]), self.mfcDCs[handle_index], (0, 0), win32con.SRCCOPY)
        self.saveBitMaps[handle_index].SaveBitmapFile(self.saveDCs[handle_index], path+"screen.bmp")
        

    def resize_img(self,img_path):
        img1 = cv2.imread(img_path, 0)
        img2 = cv2.imread('images/screen.bmp', 0)
        height, width = img1.shape[:2]
        ratio = self.device_width / img2.shape[1]
        size = (int(width/ratio), int(height/ratio))
        return cv2.resize(img1, size, interpolation = cv2.INTER_AREA)

    def Image_to_position(self,image, m = 0, similarity = 0.9):
        image_path = 'images/' + self.path + str(image) + '.bmp'
        screen = cv2.imread('images/screen.bmp', 0)
        # template = cv2.imread(image_path, 0)
        template = self.resize_img(image_path)
        methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED]
        image_x, image_y = template.shape[:2]
        result = cv2.matchTemplate(screen, template, methods[m])
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # print(max_val)
        if max_val >= similarity:
            global center
            # center = (max_loc[0] + image_y / 2, max_loc[1] + image_x / 2)
            center = (max_loc[0], max_loc[1])
            # print(center)
            return center
        else:
            return False
    
    def recursion(self,images,handle_index):

        for img,cnf in images.items():
            if img in self.notChecks[handle_index]:
                continue

            similarity = cnf.get('similarity') if cnf.get('similarity') is not None else 0.9
            # 查找图片
            if self.Image_to_position(img, m = 0,similarity=similarity) != False:
                # 找到图片看是否点击或继续递归查找
                if cnf.get('found') is not None:
                    # 立即点击
                    if type(cnf.get('found')) == int:
                        self.now_imgs[handle_index] = img
                        time.sleep(0.2)
                        offsetX = int((cnf.get('offsetX') if cnf.get('offsetX') is not None else 0) * (self.widths[handle_index] / self.device_width))
                        offsetY = int((cnf.get('offsetY') if cnf.get('offsetY') is not None else 0) * (self.heights[handle_index] / self.device_height))

                        x = int(center[0]) + random.randrange(int(50 * (self.widths[handle_index] / self.device_width))) + offsetX
                        y = int(center[1]) + random.randrange(int(25 * (self.heights[handle_index] / self.device_height))) + offsetY
                        for i in range(cnf.get('found')):
                            self.click(x,y,handle_index)
                            # print(img,x,y)
                            time.sleep(cnf.get('delay') if cnf.get('delay') is not None else 0)

                        # 单次流程不再检查
                        if cnf.get('checkAgain') is not None:
                            if cnf.get('checkAgain') == 0:
                                self.notChecks[handle_index].append(cnf.get('checkImg'))

                    else:
                        self.recursion(cnf['found'],handle_index)
            else:
                # 找不到图片看是否有操作或继续递归查找
                if cnf.get('notFound') is not None:
                    if cnf.get('notFound') == 'pass':
                        pass
                    else:
                        self.recursion(cnf['notFound'],handle_index)

    def pause(self,key):
        # print(key)
        self.wait = not self.wait
        if self.wait == True:
            print('暂停运行，按 F12 继续运行')
        else:
            print('开始运行，按 F12 暂停运行')

    def run(self):

        notFinishHandle = self.handles
        # finishHandle = []
        while True:
            while not self.wait:

                if len(notFinishHandle):
                
                    for index,handle in enumerate(notFinishHandle):

                        self.screenshot(index)

                        self.recursion(self.images,index)

                        # 一个完整流程结束，可能多次点击 
                        if self.now_imgs[index] == self.endFlag:
                            # 判断当前时间与上次一次完整流程的时间差  
                            if (datetime.now() - self.times[index]).seconds >= self.timeCost:
                                self.times[index] = datetime.now()
                                self.notChecks[index] = []
                                # 更新进度条
                                self.pbars[index].update()
                                # self.play_nums[index] += 1
                                # self.progress_manager.update(str(index), int((self.play_nums[index] / self.num_runs) * 100))
                                # 完成任务，删除待完成状态
                                if self.pbars[index].n >= self.pbars[index].total:
                                    # finishHandle.append(handle)
                                    del notFinishHandle[index]
                                # if self.play_nums[index] >= self.num_runs:
                                #     del notFinishHandle[index]

                                time.sleep(0.5 + random.random() * 0.02)
                        elif self.now_imgs[index] == self.failFlag:
                            self.failNum += 1
                            self.notChecks[index] = []
                            print('已失败 %d 次！！！' % self.failNum)
                            time.sleep(2 + random.random() * 0.02)
                else:
                    return
        
          

if __name__ == '__main__': 

        device_width=2560
        device_height=1440
        config_file_index = 0

        
            
        helper = Helper(title_name='阴阳师-网易游戏', config_file_index = config_file_index,
            device_width=device_width,device_height=device_height)
        helper.run()
        helper.__del__()
    