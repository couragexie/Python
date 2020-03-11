import requests
#from bs4 import BeautifulSoup
import time

# 引入加密、编码文件
import base64
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import json


## 获取验证码
from getStudentInfo.util import pwd_input


def getVerifiedCode():
    # 验证码地址
    link = 'http://jxgl.wyu.edu.cn/yzm?d={}'.format(time.time())  #获取当前时间
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }
    # 获取验证码对象
    verifiedNum = requests.get(link, headers = headers)
    #print('verified Cookie:{}'.format(verifiedNum.cookies.get_dict().get('JSESSIONID'))) #获取 cookies
    # 存储验证码，转成 jpg, 无法智能识别，只能人脸识别
    file = open('verifiedCode.jpg', 'wb')
    file.write(verifiedNum.content)
    return verifiedNum

# 如果text不足16位的倍数就用空格补足为16位
# 不同于JS，pycryptodome库中加密方法不做任何padding，因此需要区分明文是否为中文的情况
def add_to_16_cn(text):
    pad = 16 - len(text.encode('utf-8')) % 16
    text = text + pad * chr(pad)
    return text.encode('utf-8')

def encry(key, pw):
    # 教务处的 js 加密，对应 python 也要用相应的加密
    #var key = CryptoJS.enc.Utf8.parse('b2m5b2m5b2m5b2m5');
    #var srcs = CryptoJS.enc.Utf8.parse('xiejie..');
    #var encrypted = CryptoJS.AES.encrypt(srcs, key, {mode:CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7});

    ## python AES 加密
    mode = AES.MODE_ECB
    cryptos = AES.new(key, mode)
    pw = add_to_16_cn(pw)
    cipher_text = cryptos.encrypt(pw)
    #print('加密后的：{}'.format(b2a_hex(cipher_text))) #将密文转成16进制
    return b2a_hex(cipher_text)
# 登录
def login():
    link ='http://jxgl.wyu.edu.cn/new/login'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }
    paras = {
        'account':'',
        'pwd':''
    }
    #输入用户名
    print("账号:")
    account = input()
    #输入密码
    print("密码:")
    pwd = pwd_input()
    paras['account'] = account
    paras['pwd'] = pwd
    print()
    # 获取验证码
    verifiedCode = getVerifiedCode()
    #获取 cookies
    cookies = requests.utils.dict_from_cookiejar(verifiedCode.cookies)
    # 输入验证码
    verifiedCode = input('请输入验证码: ')
    #print('从验证码响应中获取的 Cookies:{}'.format(cookies))
    paras['verifycode'] = verifiedCode
    # 加密的密钥
    key = (verifiedCode*4).encode('utf-8')
    #print('key: %s',key)
    pw = paras['pwd']
    # 密码 AEC 加密
    secret = encry(key, pw)
    paras['pwd'] = secret
    # 登录
    login = requests.post(link, headers = headers, cookies = cookies, data = paras)
    print(login.text)
    print(login.status_code)
    print('登录后的 header:{0}'.format(login.headers))
    print('登录后的cookies:{}'.format(login.cookies))
    # 返回一个元组
    return login.status_code, cookies

def getPage(link, cookies, params):
    headers =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }
    #/xskktzd!xskktzdList.action
    # params = {
    #     # 'xnxqdm': '2019-2020-2',
    #     # 'kcdldm': '(全部)',
    #     # 'kcfldm': '(全部)',
    #     # 'kcmc': ''
    #
    # }
    #xnxqdm=2019-2020-2&kcdldm=(全部)&kcfldm=(全部)&kcmc=''
    page = requests.post(link, headers = headers, cookies = cookies, data = params)
    print("获取到页面信息: ",page.text, '\n')
    return page

#获取教务系统上课任务的数据, post请求
def getClassAssignment(cookies):
    link = 'http://jxgl.wyu.edu.cn/xskktzd!getDataList.action'
    xnxqdm = input("请输入要查询哪学期的上课任务(例：201801, 2018第一学年): ")
    params = {'xnxqdm': xnxqdm,
              'kcdldm': '',
              'kcfldm': '',
              'kcmc': '',
              'page': '1',
              'rows': '20',
              'sort': 'kcbh',
              'order': 'asc'
    }
    page = getPage(link, cookies, params)
    return page.content

# 获取整个学期的课表，
def getAllClassSchedule(cookies):
    xnxqdm = input("请输入获取指定学期的课表(例：201801, 2018第一学年):")
    link2_list = ['http://jxgl.wyu.edu.cn/xsgrkbcx!getKbRq.action?xnxqdm={0}&zc={1}'.format(xnxqdm, number)
                  for number in range(1, 20)]  ##获取课表，返回json，携带参数

    pageAll = [getPage(link, cookies, params=None)  for link in link2_list]
    #print(pageAll)
    schedules = []
    for page in  pageAll:
        #print('page:',page.text)
        scheduleInfo = json.loads(page.text)
        schedules.append(scheduleInfo[0])
        #print('schedule:',scheduleInfo[0])
    #返回全部json对象
    return schedules

# 获取课程成绩
def getGrade(cookies):
    link = 'http://jxgl.wyu.edu.cn/xskccjxx!getDataList.action'  ## post请求
    ## link3 参数：
    # xnxqdm: 201901
    # page: 1
    # rows: 20
    # sort: xnxqdm
    # order: asc
    params = {
        'xnxqdm': '',
        'page': 1,
        'rows': 20,
        'sort': 'xnxqdm',
        'order': 'asc',
    }
    xnxqdm = input("请输入指定学期的课程成绩(例：201801, 2018第一学年):")
    params['xnxqdm'] = xnxqdm
    page = getPage(link, cookies, params)
    return page

######## 主函数
# getManage()
#cookies={'JSESSIONID':'D6B6F521080E5DFE774C3029F8E279B5'}
# assignment_f = open('class_file.json','wb')
# assignment_pa20ge = getClassAssignment(cookies)
# assignment_f.write(assignment_page.content)
# grade_page = getGrade(cookies)
# grade_f = open('grade.json', 'wb')
# grade_f.write(grade_page.content)
#schedules = getAllClassSchedule(cookies)


#schedule_f = open('schedules.json', 'a')
# for schedule in schedules:
#     print()
#     schedule_f.write(json.dumps(schedule))