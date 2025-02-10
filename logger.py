import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class Logger:
    def __init__(
        self,
        name: str,
        log_file: str = 'log/app.log',
        console_level: str = 'DEBUG',
        file_level: str = 'INFO',
        max_bytes: int = 1024 * 1024,  # 1MB
        backup_count: int = 5,
        when: str = 'midnight',
        interval: int = 1
    ):
        """
        初始化日志记录器

        :param name: 日志记录器名称
        :param log_file: 日志文件路径
        :param console_level: 控制台日志级别
        :param file_level: 文件日志级别
        :param max_bytes: 单个日志文件最大大小（字节）
        :param backup_count: 保留的备份文件数量
        :param when: 时间分割单位 (S-秒, M-分, H-小时, D-天, midnight-午夜等)
        :param interval: 分割间隔
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # 设置最低日志级别

        # 防止重复添加handler
        if not self.logger.handlers:
            self._setup_handlers(log_file, console_level, file_level, max_bytes, backup_count, when, interval)

    def _setup_handlers(
        self,
        log_file: str,
        console_level: str,
        file_level: str,
        max_bytes: int,
        backup_count: int,
        when: str,
        interval: int
    ):
        """配置日志处理器"""
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, console_level.upper()))
        console_handler.setFormatter(formatter)

        # 文件处理器（按大小轮转）
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, file_level.upper()))
        file_handler.setFormatter(formatter)

        # 时间轮转文件处理器（按天分割）
        time_file_handler = TimedRotatingFileHandler(
            filename=log_file + '.time',
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding='utf-8'
        )
        time_file_handler.setLevel(logging.INFO)
        time_file_handler.setFormatter(formatter)

        # 添加处理器
        # self.logger.addHandler(console_handler)  # 控制台日志
        self.logger.addHandler(file_handler)
        self.logger.addHandler(time_file_handler)

    def debug(self, message: str):
        """记录DEBUG级别日志"""
        self.logger.debug(message)

    def info(self, message: str):
        """记录INFO级别日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """记录WARNING级别日志"""
        self.logger.warning(message)

    def error(self, message: str):
        """记录ERROR级别日志"""
        self.logger.error(message)

    def critical(self, message: str):
        """记录CRITICAL级别日志"""
        self.logger.critical(message)

    def exception(self, message: str):
        """记录异常日志"""
        self.logger.exception(message)

# # 使用示例
# if __name__ == '__main__':
#     # 初始化日志记录器
#     logger = Logger('my_app')

#     try:
#         # 不同级别的日志示例
#         logger.debug('这是DEBUG级别的消息（控制台可见）')
#         logger.info('这是INFO级别的消息')
#         logger.warning('这是WARNING级别的消息')
#         logger.error('这是ERROR级别的消息')
#         logger.critical('这是CRITICAL级别的消息')

#         # 模拟异常
#         1 / 0
#     except Exception as e:
#         logger.exception('发生异常: ')
#         logger.error(f'错误详情: {str(e)}')

#     # 模块化日志示例
#     module_logger = Logger('my_app.module')
#     module_logger.info('这是来自模块的日志消息')