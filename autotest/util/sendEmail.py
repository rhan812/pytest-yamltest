#!/usr/bin/python
# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr,formataddr


# 格式化邮件地址
def formatAddr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendMail(maile_info):
    smtp_server = maile_info.get('smtp_server')
    from_mail = maile_info.get('from_mail')
    mail_pass = maile_info.get('mail_pass')
    to_mail = maile_info.get("to_mail")
    # ['962510244@qq.com', 'zhenliang369@163.com']
    # 构造一个MIMEMultipart对象代表邮件本身
    msg = MIMEMultipart()
    # Header对中文进行转码
    msg['From'] = formatAddr('管理员 <%s>' % from_mail)
    msg['To'] = ','.join(to_mail)
    msg['Subject'] = Header('UI_自动化测试报告', 'utf-8')
    msg.attach(MIMEText(maile_info.get("body"), 'html', 'utf-8'))
    try:
        s = smtplib.SMTP()
        s.connect(smtp_server, maile_info.get("port", 25))  # "25"
        s.login(from_mail, mail_pass)
        s.sendmail(from_mail, to_mail, msg.as_string())  # as_string()把MIMEText对象变成str
        s.quit()
    except smtplib.SMTPException as e:
        print("Error: %s" % e)


email_info = {
    "smtp_server": "smtp.juxiangfen.com",
    "from_mail": "hanxingwang@juxiangfen.com",  # 发件人
    "mail_pass": "WUyan@0812",  # 密码
    "to_mail": ["809273520@qq.com", "17979704@qq.com"],  # 邮件接收人 ，可多个, 隔开
    "port": 25,  # 端口
    "body": """
    <h1>测试邮件</h1>
    <h2 style="color:red">This is a test</h1>
    """  # 邮件内容
               }

sendMail(email_info)


