from flask import Flask
from flask import request
import os
from functools import reduce
import telnetlib
import time
import json
app = Flask(__name__)

class TelnetClient:
    def __init__(self):
        self.tn = telnetlib.Telnet()

    def input(self, cmd):
        self.tn.write(cmd.encode('ascii') + b'\n')

    def get_output(self, sleep_seconds=2):
        time.sleep(sleep_seconds)
        return self.tn.read_very_eager().decode('ascii')

    def login(self, host_ip, password):
        try:
            self.tn.open(host_ip)
        except:
            print('连接失败')
        self.tn.read_until(b'Password: ')
        self.input(password)
        login_result = self.get_output()
        print(login_result)
        if 'Login incorrect' in login_result:
            print('用户名或密码错误')
            return False
        print('登陆成功')
        return True

    def logout(self):
        self.input('exit')

    def exec_cmd(self, cmd):
        self.input(cmd)
        res = self.get_output()
        print("===================")
        print(res)
        print("===================")
        return res
routerA = TelnetClient()
routerB = TelnetClient()
routerC = TelnetClient()
current = routerA


@app.route('/run', methods=['GET', 'POST'])
def run():
    router_name = request.args.get("routerName")
    cmd = request.get_data(as_text=True)
    if router_name == 'routerA':
        current = routerA
    elif router_name == 'routerB':
        current = routerB
    else:
        current = routerC
    res = current.exec_cmd(cmd)
    print(router_name)
    # s = request.get_data(as_text=True)
    # res = os.popen(s)
    # lines = res.readlines()
    # line = reduce(lambda a, b: a + b, lines)
    # res.close()
    return res


@app.route('/next', methods=['POST'])
def next():
    text = request.get_data(as_text=True)
    obj = json.loads(text)
    id = obj.nextId
    command = obj.command
    nextCommand = getCommand(id+1)
    output = current.exec_cmd(command)
    res = {"nextId": id+1, "res":output, "nextCommand": nextCommand}
    return json.dumps(res)

def getCommand(id):
    s = """
telnet 172.16.0.2
123456
en
123456
conf t
int loopback0
ip address 1.1.1.0 255.255.255.0
int s2/0
ip adderss 172.17.0.1 255.255.0.0
clock rate 128000
no shut
exit
ip route 2.2.2.0 255.255.0.0 s2/0
ip route 3.3.3.0 255.255.0.0 172.17.0.2
ip route 172.17.0.0 255.255.0.0 s2/0
ip route 172.18.0.0 255.255.0.0 172.17.0.2
exit
telnet 172.16.0.3
123456
en
123456
conf t
int loopback0
ip address 2.2.2.0 255.255.255.0
int s2/0
ip adderss 172.17.0.2 255.255.0.0
clock rate 128000
no shut
int s3/0
ip address 172.18.0.1 255.255.0.0
clock rate 128000
no shut
exit
ip route 2.2.2.0 255.255.0.0 s2/0
ip route 3.3.3.0 255.255.0.0 s3/0
ip route 172.17.0.0 255.255.0.0 s2/0
ip route 172.18.0.0 255.255.0.0 s3/0
exit
telnet 172.16.0.4
123456
en
123456
conf t
int loopback0
ip address 3.3.3.0 255.255.255.0
int s2/0
ip adderss 172.17.0.1 255.255.0.0
clock rate 128000
no shut
exit
ip route 2.2.2.0 255.255.0.0 172.18.0.1
ip route 3.3.3.0 255.255.0.0 s2/0
ip route 172.17.0.0 255.255.0.0 172.18.0.1
ip route 172.18.0.0 255.255.0.0 s2/0
exit
EOF
"""
    return s.split("\n")[id]

@app.route('/info', methods=['GET'])
def get_info():
    f = open('./config.json', encoding='utf-8')
    string = f.readlines()
    s = "".join([i.strip() for i in string])
    return s


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
    # routerA.login('172.16.0.1', '123456')
    # routerB.login('172.16.0.2',  '123456')
    # routerC.login('172.16.0.3',  '123456')

