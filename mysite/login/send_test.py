import os
from django.core.mail import send_mail, send_mass_mail,EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'


def send_one():
    send_mail(
        '来自www.liujiangblog.com的测试邮件',
        '欢迎访问www.liujiangblog.com，这里是刘江的博客和教程站点，本站专注于Python、Django和机器学习技术的分享！',
        'zhangtong_415@sina.com',
        ['874093572@qq.com'],
        fail_silently=False,
    )


def send_muple():
    msg1 = ("第一封邮件", "邮件的详细内容是：嘎嘎嘎嘎", 'zhangtong_415@sina.com', ['zhangtong_415@sina.com', "874093572@qq.com"])
    msg2 = ("第二封邮件", "邮件的详细内容是：嘿嘿欸", 'zhangtong_415@sina.com', ["874093572@qq.com"])
    send_mass_mail((msg1, msg2), fail_silently=False)

def send_html():
    subject, from_email, to = 'hello', 'zhangtong_415@sina.com', '874093572@qq.com'
    text_content = 'This is an important message1111.'
    html_content = '<p>This is an <strong>important</strong> message.</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

if __name__ == '__main__':
    # send_one()
    # send_muple()
    send_html()

    print("发送")
