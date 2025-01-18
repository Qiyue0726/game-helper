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
        helper = Helper(config_file_index = 0)
        helper.run()
        helper.__del__()
    # else:
    #     if sys.version_info[0] == 3:
    #         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  
 