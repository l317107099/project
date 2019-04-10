from django.db import models
from django.contrib.auth.models import AbstractUser
from db.Base_Models import BaseMode
# Create your models here.

class User(AbstractUser,BaseMode):

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Address(BaseMode):
    user = models.ForeignKey('User',verbose_name='用户',on_delete='CASCADE')
    addr = models.CharField(max_length=256,verbose_name='地址')
    zip_code = models.CharField(max_length=6,verbose_name='邮编')
    phone = models.CharField(max_length=11,null=True,verbose_name='电话号码')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')
    receiver = models.CharField(max_length=20,verbose_name='收件人')
    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name