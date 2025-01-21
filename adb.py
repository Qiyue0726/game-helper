import subprocess
import time
import cv2, os
from cv2 import data
from ppadb.client import Client
import adbutils
from datetime import datetime
class Helper():
    def connect_to_device(self):
        try:
            subprocess.run(["adb/adb.exe", "connect", "127.0.0.1:16384"], check=True)
            # # 创建 ADB 客户端
            client = Client(host="127.0.0.1")
            # # 获取设备列表
            devices = client.devices()
            if len(devices) == 0:
                print("No devices found")
                return
            # 获取第一个设备
            self.device = devices[0]
            # adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
            # devices = adb.device_list()
            # for device in devices:
            #     print(device.serial)
            print("Connected to 127.0.0.1:16384")
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect: {e}")
        

    def take_screenshot(self):
        try:
            timestamp = int(time.time())
            screenshot_name = f"screenshot.png"
            # subprocess.run(["adb", "shell", "screencap", "-p", f"/sdcard/{screenshot_name}"], check=True)
            # subprocess.run(["adb", "pull", f"/sdcard/{screenshot_name}", "."], check=True)
            # 改用client的方式
            path = os.path.abspath('.') + '\images\\'
            self.device.shell("screencap -p /sdcard/screenshot.png")
            self.device.pull("/sdcard/screenshot.png", f"{path}screenshot.png")
            print(f"Screenshot saved as {screenshot_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to take screenshot: {e}")

    def Image_to_position(self, image, m = 0, similarity = 0.9):
        image_path = 'images/test/test.png'
        screen = cv2.imread('images/screenshot.png', 0)
        template = cv2.imread(image_path, 0)
        methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED]
        image_x, image_y = template.shape[:2]
        result = cv2.matchTemplate(screen, template, methods[m])
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        w, h = template.shape[1], template.shape[0]
        # 对于 cv2.TM_CCORR_NORMED 我们关注最大匹配位置
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        # 绘制矩形框标记匹配区域
        cv2.rectangle(screen, top_left, bottom_right, (0, 255, 0), 2)

        # 显示结果
        cv2.imshow('Matched Image', screen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # 输出匹配结果的坐标
        print(f"Top left coordinate: {top_left}")
        print(f"Bottom right coordinate: {bottom_right}")
        print(max_val)
        if max_val >= similarity:
            global center
            # center = (max_loc[0] + image_y / 2, max_loc[1] + image_x / 2)
            center = (max_loc[0], max_loc[1])
            print(center)
            return center
        else:
            return False
    def click(self):
        self.device.shell(f"input tap {center[0]} {center[1]}")

    def run(self):
        self.connect_to_device()
        # 计算毫秒数
        start = datetime.now()
        self.take_screenshot()
        # 计算毫秒数
        end = datetime.now()
        # 计算毫秒数
        print((end - start).microseconds/1000)
        self.Image_to_position('start', m = 0, similarity = 0.6)
        # self.click()
        # self.recursion(images)
        # self.run()

if __name__ == "__main__":
    helper = Helper()
    helper.run()
    # helper.connect_to_device()
    # # 通过adb获取设备分辨率
    # device_info = subprocess.run(["adb", "shell", "wm", "size"], capture_output=True, text=True, check=True)
    # device_width, device_height = map(int, device_info.stdout.split(":")[1].strip().split("x"))
    # print(f"Device resolution: {device_width}x{device_height}")

    # helper.take_screenshot()
    # helper.Image_to_position('yy', m = 2, similarity = 0.6)
    # # 点击屏幕
    # # print(center)
    # # x = int(center[0]) + random.randrange(int(50 * (self.width / self.device_width))) + offsetX
    # # y = int(center[1]) + random.randrange(int(25 * (self.height / self.device_height))) + offsetY
                        
    # subprocess.run(["adb", "shell", "input", "tap", str(479), str(736)], check=True)

    # # 使用client的方式
    # helper.click()

    
