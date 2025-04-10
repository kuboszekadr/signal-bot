import subprocess
import logging

from src.config import app_config

logger = logging.getLogger(__name__)

class ReceiveProcess:
    def __init__(self):
        self.process = self.start_receive_process()

    def start_receive_process(self) -> subprocess.Popen:
        process = subprocess.Popen(
            [
            app_config.signal_cli_path, 
             '--log-file', app_config.signal_cli_logs_path,
             '--verbose',
             '--output=json', 'receive', 
             '--timeout', '-1'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return process

    def kill(self):
        self.process.stdout.close()
        self.process.kill()

    def __del__(self):
        self.kill()

class SendMessage:
    def send_message(self, msg: str, params: list) -> subprocess.Popen:
        args = [app_config.signal_cli_path, 'send']
        args += ['--message', msg]
        args += params
        
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()
        logger.info("STDOUT: %s", stdout)
        logger.error("STDERR: %s", stderr)
