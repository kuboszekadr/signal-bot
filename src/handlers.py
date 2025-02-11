import subprocess
import logging

logger = logging.getLogger(__name__)

class ReceiveProcess:
    def __init__(self):
        self.process = self.start_receive_process()

    def start_receive_process(self) -> subprocess.Popen:
        process = subprocess.Popen(
            ['/home/azureuser/signal-cli/signal-cli-0.13.12/bin/signal-cli', 
             '--log-file', './logs/signal-cli.log',
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
    def send_message(self, msg: str, kwargs: dict) -> subprocess.Popen:
        args = ['/home/azureuser/signal-cli/signal-cli-0.13.12/bin/signal-cli', 'send']
        args += ['--message', msg]
        args += (list(*kwargs.items()))
        
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()
        logger.info("STDOUT: %s", stdout)
        logger.error("STDERR: %s", stderr)
