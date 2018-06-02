#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = 'Jiaji Xu'

'send email'

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr


def _format_address(s):
    name, address = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), address))


from_address = 'jiajixu@qq.com'
password = 'hgvcqmblnnzlbbhj'
# to_address = 'demofamilies@gmail.com'
smtp_server = 'smtp.qq.com'

# msg = MIMEText("hello, send by xujiaji's web.", 'plain', 'utf-8')
# msg = MIMEText('<html><body><h1>XXX您好</h1>' +
#                '<p>来自网站<a href="https://www.xujiaji.org">www.xujiaji.com</a>的消息</p>' +
#                '</body></html>', 'html', 'utf-8')
# msg['From'] = _format_address("XuJiaji WEB <%s>" % from_address)
# msg['To'] = _format_address("亲爱的会员 <%s>" % to_address)
# msg['Subject'] = Header('来自xujiaji网站的消息...', 'utf-8').encode()

# server = smtplib.SMTP_SSL(smtp_server, 465)
# server.set_debuglevel(1)
# server.login(from_address, password)
# server.sendmail(from_address, [to_address], msg.as_string())
# server.quit()

# _emailServer = smtplib.SMTP_SSL()
# _emailServer.connect(smtp_server, 465)
# # _emailServer.set_debuglevel(1)
# _emailServer.login(from_address, password)


def send_comment_email(email, comment, url):
    msg = MIMEText('<html><body><h1>亲爱的会员您好！</h1>' +
                   '<p>来自xujiaji Web网站一条消息：<a href="https://www.xujiaji.org">www.xujiaji.com%s</a></p>' % url +
                   '<p>消息内容：<br>%s</p>' % comment +
                   '</body></html>', 'html', 'utf-8')

    msg['From'] = _format_address("XuJiaji WEB <%s>" % from_address)
    msg['To'] = _format_address("亲爱的会员 <%s>" % email)
    msg['Subject'] = Header('来自xujiaji网站的消息...', 'utf-8').encode()

    server = smtplib.SMTP_SSL()
    server.connect(smtp_server, 465)
    # server.set_debuglevel(1)
    server.login(from_address, password)
    server.sendmail(from_address, [email], msg.as_string())


# class SendEmail(object):
#
#     def __init__(self):
#         self.server = smtplib.SMTP_SSL(smtp_server, 465)
#         self.server.set_debuglevel(1)
#         self.server.login(from_address, password)
#
#     def send(self, address, msg):
#
#         print('================', from_address, address)
#         self.server.sendmail(from_address, [address], msg)
#         self.server.quit()
