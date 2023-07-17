import atexit
import docker
import re
import time

class BedrockServer():
    def __init__(self):
        self.client = docker.from_env()
        self.server = self.client.containers.create('05jchambers/legendary-bedrock-container:latest', ports={'19132/udp': 19132, '19132/tcp': 19132, '19133/udp': 19133, '19133/tcp': 19133}, volumes=['minecraft:/minecraft'], tty=True, detach=True, stdin_open=True)

        atexit.register(self.stop)

    def start(self):
        if self.status() != 4:
            return False

        self.server.start()
        self.sock = self.server.attach_socket(params={'stdin': 1, 'stream': 1})
        return True

    def stop(self):
        if self.status() != 1:
            return False

        self.sock._sock.send(b'stop\n')
        self.sock.close()
        return True

    def run(self, command):
        if self.status() != 1:
            return False

        command += '\n'
        self.sock._sock.send(command.encode())
        return True

    def logs(self):
        return self.server.logs().decode()

    def status(self):
        lines = self.logs().split('\r\n')
        for line in reversed(lines):
            if 'Starting Server' in line:
                return 2
            elif 'Server started' in line:
                return 1
            elif 'Server stop requested' in line:
                return 3
            elif 'Quit correctly' in line:
                return 4

        self.server.reload()
        return 2 if self.server.status == 'running' else 4

    def online(self):
        if self.status() != 1:
            return 0

        online = 0

        lines = self.logs().split('\r\n')
        for line in reversed(lines):
            if 'Player connected' in line:
                online += 1
            elif 'Player disconnected' in line:
                online -= 1

        return online


