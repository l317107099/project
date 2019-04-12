from django.shortcuts import render,reverse,redirect,HttpResponse
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
import re
from django.conf import settings

from django.core.mail import send_mail
from .models import User
# Create your views here.

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_email

class LoginView(View):
    def get(self,request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            context = {
                'checked':'checked',
                'username':username
            }
            return render(request,'index.html',context)
        else:
            context = {
                'username' : '',
                'checked' : '',
            }
            return render(request, 'login.html', context)
    def post(self,request):
        # 接收数据
        username = request.POST.get('username')
        password =request.POST.get('pwd')
        #校验数据
        # if not all([username,pwd]):
            # return render(request,'register.html',context={'errmassege':'数据不完整'})

        if not all([username, password]):
            context = {'errmessage': '数据不完整'}
            return render(request, 'login.html',context=context)
        user = authenticate(username=username,password=password)
        if user is not None:
            # user = User.objects.get(user = user)
            if user.is_active:
                login(request,user)
                next_url = request.Get.get('next',reverse('goods:index'))
                response = redirect(next_url)
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username',username,max_age=7*24*60)
                else:
                    response.delete_cookie('username')
                return response
            else:
                context = {
                    'errmessage':'该用户尚未激活,请先激活'
                }
                return render(request,'login.html',context)
        else:
            context = {
                'errmessage':'用户名或密码错误'
            }
            return render(request,'login.html',context)

class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        # 接收数据

        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        #检验数据
        if not all([username,password,cpwd,email]):
            context ={
                'errmessage': '数据输入不完整'
            }
            return render(request,'register.html',context=context)
        try:
            user = User.objects.get(username = username)
        except  User.DoesNotExist:
            user = None
        if user:
            context = {'errmessage':'用户名已经存在'}
            return render(request,'register.html',context=context)
        if password != cpwd:
            return render(request,'register.html',context={'errmessage':'两次输入的密码不一致'})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return  render(request,'register.html',context={'errmessage':'邮箱输入的格式不正确'})
        if allow != 'on':
            return  render(request,'register.html',context={'errmessage':'请阅读协议是否同意'})
        user = User.objects.create_user(username,password,email)
        user.is_active = 0
        user.save()
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()
        # html_message = '<h1>{0}, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/{1}">http://127.0.0.1:8000/user/active/{2}</a>'.format(
        #     username, token, token)
        send_register_email.delay(email,username,token)
        return HttpResponse('邮件已经发送到你的邮箱')
class ActiveView(View):
    def get(self,request,token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id = user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('goods:index'))
        except SignatureExpired as e:
            return  HttpResponse('激活链接已过期')


class LogoutView(View):
    def get(self,request):
        logout(request)
        return render(request,'goods:index')