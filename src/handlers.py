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
    def __init__(self, msg: str):
        self.msg = msg

    def send_message_to_group(self) -> subprocess.Popen:
        process = subprocess.Popen(
            ['/home/azureuser/signal-cli/signal-cli-0.13.12/bin/signal-cli', 'send', 
             "--group-id", "iwkWWvQFIbqjqoFf6g23HzUqFV4xb3QrD0eINqn5vkA=", 
             '--message', self.msg,
             '--quote-message', '1738847373395',
            # '--sticker', '8dc09d0a84804fbcc37b4b2dacbe13d6:13'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()
        logger.info("STDOUT: %s", stdout)
        logger.error("STDERR: %s", stderr)
