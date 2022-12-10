# -*- coding: utf8 -*-
import sys
import os

code_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

import logging
import json
import requests
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import datetime
from requests import Session

try:
    file = open(os.path.join(code_path, "code", "user_data.json"), "r", encoding="utf-8")
except:
    try:
        file = open(os.path.join(code_path, "user_data.json"), "r", encoding="utf-8")
    except:
        raise Exception("代码同级路径下未找到'user_data.json'文件")
user_data = json.load(file)
file.close()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Third-party SMTP service for sending alert emails. 第三方 SMTP 服务，用于发送告警邮件
mail_host = "smtp.qq.com"       # SMTP server, such as QQ mailbox, need to open SMTP service in the account. SMTP服务器,如QQ邮箱，需要在账户里开启SMTP服务

mail_user = ""  # Username 用户名
mail_pass = ""  # Password, SMTP service password. 口令，SMTP服务密码
mail_port = 465  # SMTP service port. SMTP服务端口

# The notification list of alert emails. 告警邮件通知列表
email_notify_list = {
    user_data["email"],
}


def sendEmail(fromAddr, toAddr, subject, content):
    sender = fromAddr
    receivers = [toAddr]
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(fromAddr, 'utf-8')
    message['To'] = Header(toAddr, 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("send email success")
        return True
    except smtplib.SMTPException as e:
        print(e)
        print("Error: send email fail")
        return False

def daka():
    userId = user_data["userId"]
    session = Session()

    school_home_url = ""

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': school_home_url,
        'Pragma': 'no-cache',
        'Proxy-Connection': 'keep-alive',
        'Referer': school_home_url+'/front/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    }

    r = session.post(school_home_url+'/microapp/health_daily/userInfo?userId='+userId,  headers=headers, verify=False)
    result = json.loads(r.text)
    if result["status"] != 1:
        raise Exception("登陆失败", result["msg"])
    else:
        print(result)
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    r = session.post(school_home_url+'/microapp/health_daily/alreadyReport', params={
        "userId": userId,
        "day": day
        })
    result = json.loads(r.text)
    if result["status"] == 1:
        print("已打卡")
        return

    # 获取打卡截图
    r = requests.post("/daka/getHesuan")
    jpg_base64 = r.text
    r.close()

    # 上传打卡截图
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; 22011211C Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046125 Mobile Safari/537.36 wxwork/4.0.16 ColorScheme/Light MicroMessenger/7.0.1 NetType/4G Language/zh Lang/zh',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': school_home_url,
        'X-Requested-With': 'com.tencent.wework',
        'Referer': school_home_url+'/front/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    json_data = {
        'file': 'data:image/jpeg;base64,'+jpg_base64,
        'filename': 'ScreenShot.jpg',
    }
    response = session.post(school_home_url+'/microapp/health_daily/uploadFile', headers=headers, json=json_data, verify=False)
    response = json.loads(response.text)
    jpg_url = response["domain"] + response["fileUrl"]
    print(jpg_url)

    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; 22011211C Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046027 Mobile Safari/537.36 wxwork/4.0.6 ColorScheme/Light MicroMessenger/7.0.1 NetType/WIFI Language/zh Lang/zh',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': school_home_url,
        'X-Requested-With': 'com.tencent.wework',
        'Referer': school_home_url+'/front/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    json_data = {
    'stuImgUrl': jpg_url,
    'isInThreeDay': '是',
    'teacherImgUrl': None,
    'isInTwoDay': None,
    'noTwoDayRmk': None,
    'noThreeDayRmk': None,
    'healthCodeState': '绿',
    'teacherOrStu': '学生',
    'geliState': None,
    'resideArea': None,
    'checkState': '是',
    'checkStateRmk': None,
    'isHasDangerous': None,
    'isHasDangerousRmk': None,
    'address': user_data["address"],
    'locationErrorExplain': None,
    'province': user_data["province"],
    'city': user_data["city"],
    'county': user_data["county"],
    'distance': 2,
    'longitude': user_data["longitude"],
    'latitude': user_data["latitude"],
    'temperature': '37.2',
    'healthCondition': '正常',
    'healthConditionExplain': None,
    'familyCondition': None,
    'familyConditionExplain': None,
    'recentlyGoArea': None,
    'recentlyGoAreaExplain': None,
    'ifContactCase': '无',
    'ifContactCaseExplain': None,
    'ifContactAreaBackPerson': None,
    'ifContactAreaBackPersonExplain': None,
    'ifContactRjry': '无',
    'ifContactRjryExplain': None,
    'ifReturnToSchool': '已在校',
    'ifReturnToSchoolExplain': None,
    'billingContactName': user_data["billingContactName"],
    'billingContactNameTel': user_data["billingContactNameTel"],
    'specialSituation': None,
    'ifFromToFocusArea': None,
    'ifFromToFocusAreaExplain': '',
    'fileUrl': '',
    'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'plusinfo': 'Mozilla/5.0 (Linux; Android 12; 22011211C Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046125 Mobile Safari/537.36 wxwork/4.0.16 ColorScheme/Light MicroMessenger/7.0.1 NetType/WIFI Language/zh Lang/zh'}

    r = session.post(school_home_url+'/microapp/health_daily/report', headers=headers, json=json_data, verify=False)
    result = json.loads(r.text)
    session.close()
    if result["status"] != 1:
        raise Exception("打卡失败", result["msg"])
    else:
        print(result)


def handler(event, context):
    try:
        daka()
    except Exception as e:
        for toAddr in email_notify_list:
            sendEmail(mail_user, toAddr, "企业微信没打卡", str(e))
        return


if __name__ == '__main__':
    handler("", "")
