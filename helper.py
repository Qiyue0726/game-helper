# -*- coding:utf-8 -*-
from __future__ import print_function
import ctypes, sys, time, os, random, json
import cv2
import win32gui,win32ui,win32api,win32con
from tqdm import tqdm


class Helper():

    def __init__(self,title_name='阴阳师-网易游戏',num_runs=100,config_file = "yuhun",
                device_width = 2560,device_height= 1440,is_flag='Y'):

        self.device_width = device_width
        self.device_height = device_height
        self.is_flag = is_flag
        self.handle = win32gui.FindWindow(None,title_name)

        #获取句柄窗口的大小信息
        left, top, right, bot = win32gui.GetWindowRect(self.handle)
        self.width = right - left
        self.height = bot - top
        # print(width,height)
        #返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        self.handleDC = win32gui.GetWindowDC(self.handle)
        #创建设备描述表
        self.mfcDC = win32ui.CreateDCFromHandle(self.handleDC)
        #创建内存设备描述表
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        #创建位图对象准备保存图片
        self.saveBitMap = win32ui.CreateBitmap()
        #为bitmap开辟存储空间
        self.saveBitMap.CreateCompatibleBitmap(self.mfcDC,self.width,self.height)

        # Initialize configuration for target pixel and clicking area
        print("配置文件config_xxx.txt(默认%s，输入xxx)：" % config_file, end="")
        config_file_input = input()
        config_file = "./config/config_" + (config_file_input if config_file_input != "" else config_file) + ".json" 

        with open(config_file,'r') as f:
            config = json.load(f)
            self.path = config.pop('path')
            self.endFlag = config.pop('endFlag')
            self.images = config
        
        # 是否启动标记一号位
        print(r"是否标记一号位 Y/N (默认%s)：" % is_flag, end="")
        is_flag_input = input()
        self.is_flag = is_flag_input if is_flag_input != "" else is_flag


        # Get the input for total running time
        print("运行次数(默认%d)：" % num_runs, end="")
        num_runs_input = input()
        num_runs = int(num_runs_input) if num_runs_input != "" else num_runs
        # Initialize progressing bar with the total running times
        self.pbar = tqdm(total=num_runs, ascii=True)
    
    def __del__(self):
        self.pbar.close()
        # Remove DCs
        win32gui.DeleteObject(self.saveBitMap.GetHandle())
        self.saveDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.handle, self.handleDC)


    def click(self,x, y):
        long_position = win32api.MAKELONG(x,y)

        win32api.SendMessage(self.handle, win32con.WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
        time.sleep(0.01 + random.random() * 0.02)
        win32api.SendMessage(self.handle, win32con.WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起



    def screenshot(self):
        path = os.path.abspath('.') + '\images\\'

        #将截图保存到saveBitMap中
        self.saveDC.SelectObject(self.saveBitMap)
        #保存bitmap到内存设备描述表
        self.saveDC.BitBlt((0,0), (self.width,self.height), self.mfcDC, (0, 0), win32con.SRCCOPY)
        self.saveBitMap.SaveBitmapFile(self.saveDC, path+"screen.bmp")
        

    def resize_img(self,img_path):
        img1 = cv2.imread(img_path, 0)
        img2 = cv2.imread('images/screen.bmp', 0)
        height, width = img1.shape[:2]
        ratio = self.device_width / img2.shape[1]
        size = (int(width/ratio), int(height/ratio))
        return cv2.resize(img1, size, interpolation = cv2.INTER_AREA)

    def Image_to_position(self,image, m = 0):
        image_path = 'images/' + self.path + str(image) + '.bmp'
        screen = cv2.imread('images/screen.bmp', 0)
        # template = cv2.imread(image_path, 0)
        template = self.resize_img(image_path)
        methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED]
        image_x, image_y = template.shape[:2]
        result = cv2.matchTemplate(screen, template, methods[m])
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # print(max_val)
        if max_val > 0.93:
            global center
            # center = (max_loc[0] + image_y / 2, max_loc[1] + image_x / 2)
            center = (max_loc[0], max_loc[1])
            # print(center)
            return center
        else:
            return False
    
    def recursion(self,images):
        # 检测是否存在图片，存在则进一步检测看是否可以直接点击，不行则开始递归检测
        for img in images:
            if self.Image_to_position(img, m = 0) != False:
                # 点击后延时
                if(images[img] == 1):
                    self.now_img = img
                    time.sleep(0.2)
                    x = int(center[0]) + random.randrange(int(50 * (self.width / self.device_width)))
                    y = int(center[1]) + random.randrange(int(25 * (self.height / self.device_height)))
                    self.click(x,y)
                    time.sleep(2)
                # 点击后立即继续
                elif(images[img] == 2):
                    self.now_img = img
                    time.sleep(0.2)
                    x = int(center[0]) + random.randrange(int(50 * (self.width / self.device_width)))
                    y = int(center[1]) + random.randrange(int(25 * (self.height / self.device_height)))
                    self.click(x,y)
                else:
                    self.recursion(images[img])

    # 标记
    def flag(self):
        # 检测是否战斗中
        if self.Image_to_position('object', m = 0) != False:
            # 检测是否有标记
            if self.Image_to_position('flag', m = 0) != False:
                pass
            else:
                # 找到式神并标记
                if self.Image_to_position('object', m = 0) != False:
                    x = int(center[0]) +  random.randrange(int(25 * (self.width / self.device_width))) + int(150 * (self.width / self.device_width))
                    y = int(center[1]) + random.randrange(int(25 * (self.height / self.device_height))) - int(30 * (self.width / self.device_width))
                    self.click(x,y)



    def run(self):

        self.now_img = ''
        while self.pbar.n < self.pbar.total:

            while True:
                self.screenshot()

                if self.is_flag == 'Y' or self.is_flag == 'y':
                    self.flag()

                self.recursion(self.images)
                        
                if self.now_img == self.endFlag:
                    break

            self.pbar.update()
            time.sleep(0.5 + random.random() * 0.02)
        
          

def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

if __name__ == '__main__': 
    if is_admin():

        device_width=2560
        device_height=1440
        config_file = "yuhun"

        
            
        helper = Helper(title_name='阴阳师-网易游戏', config_file = config_file,
            device_width=device_width,device_height=device_height)
        helper.run()
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  
   
