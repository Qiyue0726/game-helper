from helper import Helper
import subprocess

# def is_admin():
#         try:
#             return ctypes.windll.shell32.IsUserAnAdmin()
#         except:
#             return False

if __name__ == '__main__': 
    # if is_admin():

        subprocess.run(["adb/adb.exe", "connect", "127.0.0.1:16384"], check=True)
        flag = True
        helper = Helper(config_file_index = 0)
        helper.run()
        while flag:
            con = input("是否继续运行其它任务？(Y/N):")
            continueFlag = "Y"
            continueFlag = con if con != "" else continueFlag
            if continueFlag == 'y' or continueFlag == "Y":
                helper.pbar.close()
                helper.wait = False
                helper.load_config(0, 100)
                helper.run()
            else:
                helper.__del__()
                del helper
                flag = False
    # else:
    #     if sys.version_info[0] == 3:
    #         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  
 