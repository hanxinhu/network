from flask import Flask
from flask import request, make_response
import os
from functools import reduce
import telnetlib
import time
import json
from flask_cors import *

app = Flask(__name__)
CORS(app, resources=r'/*', supports_credentials=True)


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
    router_name = request.args.get("routerName")
    text = request.get_data(as_text=True)
    obj = json.loads(text)
    id = obj.nextId
    command = obj.command
    index = 0
    if router_name == 'routerA':
        index = 0
    elif router_name == 'routerB':
        index = 1
    else:
        index = 2
    nextCommand, sum = getCommand(id + 1)
    output = current.exec_cmd(command)
    res = {"nextId": (id + 1) % sum, "res": output, "nextCommand": nextCommand}
    return json.dumps(res)


def getCommand(id, index=0):
    s1 = """
telnet 172.16.0.2
123456
en
123456
conf t
int loopback0
ip address 1.1.1.0 255.0.0.0
int s0/0/0
ip address 172.17.0.1 255.255.0.0
clock rate 128000
no shut
exit
ip route 2.2.2.0 255.255.255.0 s0/0/0
ip route 3.3.3.0 255.255.255.0 172.17.0.2
ip route 172.17.0.0 255.255.0.0 s0/0/0
ip route 172.18.0.0 255.255.0.0 172.17.0.2
exit
"""
    s2 = """
telnet 172.16.0.3
123456
en
123456
conf t
int loopback0
ip address 2.2.2.0 255.0.0.0
int s0/0/0
ip address 172.17.0.2 255.255.0.0
clock rate 128000
no shut
int s0/0/1
ip address 172.18.0.1 255.255.0.0
clock rate 128000
no shut
exit
ip route 2.2.2.0 255.255.255.0 s0/0/0
ip route 3.3.3.0 255.255.255.0 s0/0/1
ip route 172.17.0.0 255.255.0.0 s0/0/0
ip route 172.18.0.0 255.255.0.0 s0/0/1
exit
"""
    s3 = """
telnet 172.16.0.4
123456
en
123456
conf t
int loopback0
ip address 3.3.3.0 255.0.0.0
int s0/0/0
ip address 172.18.0.2 255.255.0.0
clock rate 128000
no shut
exit
ip route 2.2.2.0 255.255.255.0 172.18.0.1
ip route 3.3.3.0 255.255.255.0 s0/0/0
ip route 172.17.0.0 255.255.0.0 172.18.0.1
ip route 172.18.0.0 255.255.0.0 s0/0/0
exit
"""
    l = list()
    l.append(s1.split("\n"))
    l.append(s2.split("\n"))
    l.append(s3.split("\n"))
    length = len(l[index % len(l)])
    return l[index % len(l)][id % length], length


@app.route('/info', methods=['GET'])
def get_info():
    f = open('./config.json', encoding='utf-8')
    string = f.readlines()
    s = "".join([i.strip() for i in string])
    return s


@app.route('/validate', methods=['GET'])
def validate():
    # router = TelnetClient()
    # router.login('172.19.241.224', 'root', 'Nju123456')
    # router.exec_cmd("show ip route")
    # output = router.get_output()
    # res = False
    # if "1.0.0.0.24" in output and "2.0.0.0/24" in output and "3.0.0.0/24" in output and "172.16.0.0/16" in output and "172.16.0.0/17" in output and "172.16.0.0/18" in output:
    #     res = True
    #
    # if res:
    #     router.exec_cmd("ping 172.17.0.1")
    #     output = router.get_output()
    #     if not ("Success rate is 100 percent (5/5)" in output):
    #         res = False
    #
    # if res:
    #     router.exec_cmd("ping 172.18.0.2")
    #     output = router.get_output()
    #     if not ("Success rate is 100 percent (5/5)" in output):
    #         res = False
    #
    # if res:
    #     router.exec_cmd("ping 172.17.0.2")
    #     output = router.get_output()
    #     if not ("Success rate is 100 percent (5/5)" in output):
    #         res = False
    #
    # if res:
    #     router.exec_cmd("show int s2/0")
    #     output = router.get_output()
    #     if not ("Serial2/0 is up" in output):
    #         res = False
    #
    # if res:
    #     router.exec_cmd("ping 2.2.2.0")
    #     output = router.get_output()
    #     if not ("Success rate is 100 percent (5/5)" in output):
    #         res = False
    #
    # if res:
    #     router.exec_cmd("ping 3.3.3.0")
    #     output = router.get_output()
    #     if not ("Success rate is 100 percent (5/5)" in output):
    #         res = False
    #
    # if res:
    #     router.exec_cmd("traceroute 3.3.3.0")
    #     output = router.get_output()
    #     if not ("172.17.0.2" in output or "172.18.0.2" in output):
    #         res = False

    return "true"


@app.after_request
def after(resp):
    '''
    被after_request钩子函数装饰过的视图函数
    ，会在请求得到响应后返回给用户前调用，也就是说，这个时候，
    请求已经被app.route装饰的函数响应过了，已经形成了response，这个时
    候我们可以对response进行一些列操作，我们在这个钩子函数中添加headers，所有的url跨域请求都会允许！！！
    '''
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
    # routerA.login('172.16.0.1', '123456')
    # routerB.login('172.16.0.2',  '123456')
    # routerC.login('172.16.0.3',  '123456')
