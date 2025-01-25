from helper import Helper
import subprocess, os

def connect_device_with_port_attempts(ip, base_port):
    max_attempts = 5
    for attempt in range(max_attempts):
        current_port = base_port + attempt
        try:
            # 获取当前脚本所在的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建 adb 的相对路径
            adb_relative_path = os.path.join(current_dir, 'adb', 'adb.exe')
            # 构建 ADB 连接命令
            command = f"{adb_relative_path} connect {ip}:{current_port}"
            print(command)
            # 执行 ADB 命令
            result = subprocess.run(command, shell=True, text=True, capture_output=True, encoding='utf-8')
            # 手动检查返回码
            if result.returncode == 0:
                # 检查命令输出是否包含成功连接的信息
                if "connected to" in result.stdout:
                    print(f"成功连接到设备 {ip}:{current_port}")
                    return True
                else:
                    print(f"尝试连接 {ip}:{current_port} 失败: {result.stderr}")
            else:
                print(f"尝试连接 {ip}:{current_port} 时发生错误: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"尝试连接 {ip}:{current_port} 时发生错误: {e.stderr}")
    # 如果超过最大尝试次数仍未成功连接，则抛出错误
    raise ConnectionError(f"经过 {max_attempts} 次尝试后，无法连接到设备 {ip}。")


if __name__ == '__main__': 
        # subprocess.run(["adb/adb.exe", "connect", "127.0.0.1:16384"], check=True)
        device_ip = "127.0.0.1"
        start_port = 16384
        try:
            connect_device_with_port_attempts(device_ip, start_port)

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
        except ConnectionError as e:
            print(e)
            input("按任意键退出...")

