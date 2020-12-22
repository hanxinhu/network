from flask import Flask
from flask import request
import os
from functools import reduce
import telnetlib
import time
app = Flask(__name__)


class TelnetClient:
    def __init__(self):
        self.tn = telnetlib.Telnet()

    def input(self, cmd):
        self.tn.write(cmd.encode('ascii') + b'\n')

    def get_output(self, sleep_seconds=2):
        time.sleep(sleep_seconds)
        return self.tn.read_very_eager().decode('ascii')

    def login(self, host_ip, username, password):
        try:
            self.tn.open(host_ip)
        except:
            print('连接失败')
        self.tn.read_until(b'login: ')
        self.input(username)
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


@app.route('/run', methods=['GET', 'POST'])
def run():
    router_name = request.args.get("routerName")
    cmd = request.get_data(as_text=True)
    if router_name == 'routerA':
        res = routerA.exec_cmd(cmd)
    elif router_name == 'routerB':
        res = routerB.exec_cmd(cmd)
    else:
        res = routerC.exec_cmd(cmd)
    print(router_name)
    # s = request.get_data(as_text=True)
    # res = os.popen(s)
    # lines = res.readlines()
    # line = reduce(lambda a, b: a + b, lines)
    # res.close()
    return res


@app.route('/info', methods=['GET'])
def get_info():
    f = open('./config.json', encoding='utf-8')
    string = f.readlines()
    s = "".join([i.strip() for i in string])
    return s

routerA = TelnetClient()
routerB = TelnetClient()
routerC = TelnetClient()
if __name__ == '__main__':
    app.run(debug=True, port=5000)
    # routerA.login('172.19.241.224', 'root', 'Nju123456')
    # routerB.login('172.19.241.224', 'root', 'Nju123456')
    # routerC.login('172.19.241.224', 'root', 'Nju123456')

