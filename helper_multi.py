# -*- coding:utf-8 -*-
from __future__ import print_function
import ctypes, sys, time, os, random, json
import keyboard
import cv2
from cv2 import data
import win32gui,win32ui,win32api,win32con
from tqdm import tqdm
from datetime import datetime


class Helper():

    def __init__(self,title_name='阴阳师-网易游戏',num_runs=100,config_file_index = 0,
                device_width = 2560,device_height= 1440):

        self.title_name = title_name
        self.device_width = device_width
        self.device_height = device_height
        self.notCheck = []
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

        if len(handle) > 1:
            print('请输入需要设置为队长/开车的窗口索引（左上角标题序号）:')
            self.main_handle_index = input()
            
        
        for index,handle in enumerate(self.handles):
            win32gui.SetWindowText(handle, self.title_name + ' - ' + str(index + 1))
            #获取句柄窗口的大小信息
            left, top, right, bot = win32gui.GetWindowRect(self.handle)
            width = right - left
            height = bot - top
            # print(width,height)
            #返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
            handleDC = win32gui.GetWindowDC(handle)
            #创建设备描述表
            mfcDC = win32ui.CreateDCFromHandle(handleDC)
            #创建内存设备描述表
            saveDC = self.mfcDC.CreateCompatibleDC()
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
        print("运行次数(默认%d)：" % num_runs, end="")
        num_runs_input = input()
        num_runs = int(num_runs_input) if num_runs_input != "" else num_runs

        print()
        print('%s 开始运行 %s' % ('*'*20,'*'*20))
        print()
        print('配置文件：%s' % config_file)
        print('运行次数：%d' % num_runs)
        print('按下 F12 暂停/运行脚本')
        print()

        # Initialize progressing bar with the total running times
        self.pbar = tqdm(total=num_runs, ascii=True)

        keyboard.on_press_key("F12", self.pause)
    
    def __del__(self):
        self.pbar.close()
        for index,handle in enumerate(self.handles):
            win32gui.SetWindowText(handle,self.title_name)
            # Remove DCs
            win32gui.DeleteObject(self.saveBitMaps[index].GetHandle())
            self.saveDCs[index].DeleteDC()
            self.mfcDCs[index].DeleteDC()
            win32gui.ReleaseDC(handle, self.handleDCs[index])


    def click(self,x, y, handle_index):
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
    
    def recursion(self,images):

        for img,cnf in images.items():
            if img in self.notCheck:
                continue

            similarity = cnf.get('similarity') if cnf.get('similarity') is not None else 0.9
            # 查找图片
            if self.Image_to_position(img, m = 0,similarity=similarity) != False:
                # 找到图片看是否点击或继续递归查找
                if cnf.get('found') is not None:
                    # 立即点击
                    if type(cnf.get('found')) == int:
                        self.now_img = img
                        time.sleep(0.2)
                        offsetX = int((cnf.get('offsetX') if cnf.get('offsetX') is not None else 0) * (self.width / self.device_width))
                        offsetY = int((cnf.get('offsetY') if cnf.get('offsetY') is not None else 0) * (self.height / self.device_height))

                        x = int(center[0]) + random.randrange(int(50 * (self.width / self.device_width))) + offsetX
                        y = int(center[1]) + random.randrange(int(25 * (self.height / self.device_height))) + offsetY
                        for i in range(cnf.get('found')):
                            self.click(x,y)
                            # print(img,x,y)
                            time.sleep(cnf.get('delay') if cnf.get('delay') is not None else 0)

                        # 单次流程不再检查
                        if cnf.get('checkAgain') is not None:
                            if cnf.get('checkAgain') == 0:
                                self.notCheck.append(cnf.get('checkImg'))

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
        # print(key)
        self.wait = not self.wait
        if self.wait == True:
            print('暂停运行，按 F12 继续运行')
        else:
            print('开始运行，按 F12 暂停运行')

    def run(self):

        self.now_img = ''
        self.time = datetime.now()
        while self.pbar.n < self.pbar.total:
            while True:
                while not self.wait:
                    self.screenshot()

                    self.recursion(self.images)

                    # 一个完整流程结束，可能多次点击 
                    if self.now_img == self.endFlag:
                        # 判断当前时间与上次一次完整流程的时间差  
                        if (datetime.now() - self.time).seconds >= self.timeCost:
                            self.time = datetime.now()
                            self.notCheck = []
                            self.pbar.update()
                            time.sleep(0.5 + random.random() * 0.02)
                    elif self.now_img == self.failFlag:
                        self.failNum += 1
                        self.notCheck = []
                        print('已失败 %d 次！！！' % self.failNum)
                        time.sleep(2 + random.random() * 0.02)
        
          

def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

if __name__ == '__main__': 
    # if is_admin():

        device_width=2560
        device_height=1440
        config_file_index = 0

        
            
        helper = Helper(title_name='阴阳师-网易游戏', config_file_index = config_file_index,
            device_width=device_width,device_height=device_height)
        helper.run()
    # else:
    #     if sys.version_info[0] == 3:
    #         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  
   
