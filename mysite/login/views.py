from django.shortcuts import render, redirect
from .models import User, ConfirmString
from . import forms
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import JsonResponse
import hashlib, datetime


# Create your views here.
def index(request):
    return render(request, "login/index.html")
    pass


def hash_code(value, alt="mysite"):
    h = hashlib.sha256()
    value += alt
    h.update(value.encode())
    return h.hexdigest()
    pass


# def login(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         massage = "请检查填写的内容!!!"
#
#         if username.strip() and password:
#             try:
#                 user = User.objects.get(name=username)
#             except:
#                 massage = "用户名不存在!!!"
#                 return render(request, "login/login.html",{"massage":massage})
#             if user.passsword == password:
#                 print(username, password)
#                 return redirect("/login/index/")
#             else:
#                 massage = "密码不正确!!!"
#                 return render(request, "login/login.html", {"massage": massage})
#         else:
#             return render(request, "login/login.html", {"massage": massage})
#     return render(request, "login/login.html")
#     pass
def login(request):
    if request.session.get("is_llgin", None):
        return redirect("/login/index/")
    if request.is_ajax():  # 请求ajax则返回新的image_url和key
        print("login : request.is_ajax(")
        result = dict()
        result['key'] = CaptchaStore.generate_key()
        result['image_url'] = captcha_image_url(result['key'])
        print("result['key']:", result['key'])
        print("result['image_url']:", result['image_url'])
        return JsonResponse(result)
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        massage = "请检查填写的内容!!!"

        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = User.objects.get(name=username)
            except:
                massage = "用户名不存在!!!"
                return render(request, "login/login.html", locals())

            if not user.has_confirmed:
                massage = "用户还未经过邮箱确认"
                return render(request, "login/login.html", locals())

            if user.passsword == hash_code(password):
                print(username, password)
                request.session["is_login"] = True
                request.session["user_id"] = user.id
                request.session["user_name"] = user.name
                return redirect("/login/index/")
            else:
                massage = "密码不正确!!!"
                return render(request, "login/login.html", locals())
        else:
            return render(request, "login/login.html", locals())
    login_form = forms.UserForm()
    return render(request, "login/login.html", locals())
    pass


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    ConfirmString.objects.create(code=code, user=user)
    return code


from mysite.settings.base import CONFIRM_DAYS, EMAIL_HOST_USER


def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = '来自www.liujiangblog.com的注册确认邮件'

    text_content = '''感谢注册www.liujiangblog.com，这里是刘江的博客和教程站点，专注于Python、Django和机器学习技术的分享！\
                        如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''
    html_content = '''
                        <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                        这里是刘江的博客和教程站点，专注于Python、Django和机器学习技术的分享！</p>
                        <p>请点击站点链接完成注册确认！</p>
                        <p>此链接有效期为{}天！</p>
                        '''.format('127.0.0.1:8000/login', code, CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def register(request):
    if request.session.get("is_login", None):
        return redirect("/login/index")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        print("message1:", message)
        if register_form.is_valid():
            username = register_form.cleaned_data.get("username")
            password1 = register_form.cleaned_data.get("password1")
            password2 = register_form.cleaned_data.get("password2")
            email = register_form.cleaned_data.get("email")
            sex = register_form.cleaned_data.get("sex")
            print("username:", username)
            print("password1:", password1)
            print("password2:", password2)
            if not password1 == password2:
                message = "密码不一致！"
                print("message2:", message)
                return render(request, "login/register.html", locals())
            same_username = User.objects.filter(name=username)
            if same_username:
                message = "该用户名已经被注册！"
                print("message3:", message)
                return render(request, "login/register.html", locals())
            same_mail = User.objects.filter(email=email)
            if same_mail:
                message = "该邮箱已经被注册！"
                print("message3:", message)
                return render(request, "login/register.html", locals())
            new_user = User()
            new_user.name = username
            new_user.passsword = hash_code(password1)
            new_user.email = email
            new_user.sex = sex
            new_user.save()

            code = make_confirm_string(new_user)
            send_email(email, code)
            return redirect("/login/login/")
        print("register_form.errors")
        print(register_form.errors)
        return render(request, "login/register.html", locals())
    register_form = forms.RegisterForm()
    return render(request, "login/register.html", locals())
    pass


def user_confirm(request):
    code = request.GET.get("code", None)
    message = ""
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = "无效请求"
        return render(request, 'login/confirm.html', locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(CONFIRM_DAYS):
        confirm.user.delete()
        return render(request, "login/confirm.html", locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = "感谢确认，请使用账户登陆"
        return render(request, "login/confirm.html", locals())
    pass


def logout(request):
    if not request.session.get("is_login", None):
        return redirect("/login/login")
    request.session.flush()
    return redirect("/login/login")
    pass
