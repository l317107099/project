from django.db import models
from  db.Base_Models import BaseMode
from tinymce.models import HTMLField
# Create your models here.


class GoodsSKU(BaseMode):
    statu =(
                (0,'上架'),
                (1,'下架')
            )
    type = models.ForeignKey('GoodsType',verbose_name='商品类型',on_delete='CASCADE')
    goods = models.ForeignKey('Goods',verbose_name='商品SPU表',on_delete='CASCADE')
    name = models.CharField(max_length=20,verbose_name='商品名称')
    price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')
    unite = models.CharField(max_length=10,verbose_name='商品单位')
    image = models.ImageField(upload_to='goods',verbose_name='商品图片')
    desc = models.CharField(max_length=256,verbose_name='商品简介')
    sales= models.IntegerField(default=0,verbose_name='商品销量')
    stock = models.IntegerField(default=1,verbose_name='商品库存')
    status = models.SmallIntegerField(default=0,choices=statu,verbose_name='上架状态')

    class Meta:
        db_table = 'df_goods_sku'
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class GoodsType(BaseMode):
    name = models.CharField(max_length=20,verbose_name='商品种类名称')
    logo = models.CharField(max_length=20,verbose_name='商品小图标')
    image = models.ImageField(upload_to='type',verbose_name='类型图片')

    class Meta:
        db_table = 'df_goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Goods(BaseMode):
    name = models.CharField(max_length=20,verbose_name='商品SPU')
    detail = HTMLField(blank=True,verbose_name = '商品详情')

    class Meta:
        db_table = 'df_goods'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name


class GoodsImage(BaseMode):
    sku = models.ForeignKey('GoodsSKU',verbose_name='商品',on_delete='CASCADE')
    image = models.ImageField(upload_to='goods',verbose_name='图片地址')

    class Meta:
        db_table = 'df_goods_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name


class IndexGoodsBanner(BaseMode):
    sku = models.ForeignKey('GoodsSKU',verbose_name='商品',on_delete='CASCADE')
    image = models.ImageField(upload_to='banner',verbose_name='图片')
    index = models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table = 'df_index_goods_banner'
        verbose_name = '首页轮播商品'
        verbose_name_plural = verbose_name


class IndexTypeGoodsBanner(BaseMode):
    DISPLAY_TYPE_CHOICES = (
        (0, "标题"),
        (1, "图片")
    )

    type = models.ForeignKey('GoodsType',verbose_name='商品类型',on_delete='CASCADE')
    sku = models.ForeignKey('GoodsSKU',verbose_name='商品SKU',on_delete='CASCADE')
    display_type = models.SmallIntegerField(default=1,choices=DISPLAY_TYPE_CHOICES,verbose_name='展示类型')
    index = models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table = 'df_type _goods_banner'
        verbose_name = '分类商品展示'
        verbose_name_plural = verbose_name


class IndexPromotionBanner(BaseMode):
    name = models.CharField(max_length=20,verbose_name='活动名称')
    url = models.CharField(max_length=256,verbose_name='活动链接')
    image = models.ImageField(upload_to='banner',verbose_name='活动图片')
    index = models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table = 'df_index_promotion_banner'
        verbose_name = '主页促销活动'
        verbose_name_plural = verbose_name