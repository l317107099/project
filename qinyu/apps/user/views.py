from django.shortcuts import render,reverse,redirect,HttpResponse
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
import re
from django.conf import settings

from django.core.mail import send_mail
from .models import User,Address
from goods.models import GoodsSKU
# Create your views here.

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_email
from django_redis import get_redis_connection

from utils.mixin import LoginRequiredMixin


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
        # user = authenticate(username=username,password=password)
        # 业务处理:登录校验
        user = authenticate(username=username, password=password)
        # if user is not None:
        if user:
            # user = User.objects.get(user = user)
            if user.is_active:
                login(request,user)
                next_url = request.GET.get('next',reverse('goods:index'))
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
        user = User.objects.create_user(username=username,password=password,email=email)
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
        return render(request,'index.html')

class SiteView(LoginRequiredMixin, View):
    def get(self,request):
        user = request.user
        try:
            address = Address.objects.get(user=user,is_default=True)
        except:
            address = None
        context = {
            'address' : address
        }
        return render(request,'user_center_site.html',context=context)

    def post(self,request):
        # 接收数据
        receiver = request.POST.get('receiver')
        adds = request.POST.get('adds')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 校验数据
        if not all([receiver,adds,phone]):
            return render(request,'user_center_site.html',context={'errmessage':'数据不完整'})
        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request,'user_center_site.html',context={'errmessage':'手机格式不正确'})

        user = request.user

        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default =True
        Address.objects.create(
            user= user,
            phone = phone,
            is_default = is_default,
            addr = adds,
            receiver = receiver,
            zip_code = zip_code
        )

        return redirect(reverse('user:site'))

class InfoView(LoginRequiredMixin,View):
    def get(self,request):
        user = request.user
        try:
            address = Address.objects.get(user=user,is_default=True)
        except:
            address = None
        conn = get_redis_connection('default')
        history_key = 'history_{0}'.format(user.id)
        history_content = conn.lrange(history_key,0,4)
        good_lis = []
        for his in history_content:
            skus = GoodsSKU.objects.get(id=his)
            good_lis.append(skus)
        context = {
            'address' : address,
            'good_lis' : good_lis,
        }

        return render(request,'user_center_info.html',context=context)