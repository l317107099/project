from django.shortcuts import render,redirect,reverse
from django.views import View
from django.core.cache import cache
# from django.contrib.auth import authenticate
from django_redis import get_redis_connection
from .models import  GoodsSKU,GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
# Create your views here.
from django.core.paginator import Paginator


class IndexView(View):
    def get(self,request):
        # return render(request,'index.html')
        #获取缓存的数据
        contents = cache.get('index_page_data')
        if contents is None:
            # 获取商品的类型
            types = GoodsType.objects.filter()
            # 获取首页轮播
            goods_banners = IndexGoodsBanner.objects.filter()
            # 获取活动
            promotion_banners = IndexPromotionBanner.objects.filter()
            # 根据类型获取图片和文字信息
            for type in types:
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by('index')
                type.image_banners = image_banners
                type.title_banners = title_banners

            context = {
                'types':types,
                'goods_banners':goods_banners,
                'promotion_banners':promotion_banners
            }
            # cache.set('index_page_data',context,3600)
        # 获取购物车的数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_{0}'.format(user.id)
            cart_count = conn.hlen(cart_key)

        context.update(cart_count=cart_count)

        return render(request,'index.html',context=context)

class DetailView(View):
    def get(self,request,goods_id):
        #接收数据
        #处理数据
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except:
            return redirect(reverse('goods:index'))

        #获取商品分类信息
        types = GoodsType.objects.filter()

        #获取新品详细
        new_skus = GoodsSKU.objects.filter(type= sku.type).order_by('-create_time')[:2]

        #获取同一个商品其它种类的规格
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_{0}'.format(user.id)
            count = conn.hlen(cart_key)

            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_{0}'.format(user.id)
            conn.lrem(history_key,0,goods_id)
            conn.lpush(history_key,goods_id)
            conn.ltrim(history_key,0,4)
        context ={
            'sku' : sku,
            'types' : types,
            'new_skus' : new_skus,
            'same_spu_skus':same_spu_skus,
            'cart_count' :cart_count

        }
        return render(request,'detail.html',context=context)

class ListView(View):
    def get(self,request,type_id,page):
        # 获取商品类型
        # 校验数据
        try:
            type = GoodsType.objects.get(id = type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))
        # 另一个模块
        types = GoodsType.objects.all()
        #排序方式get传参
        # 接收数据
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type = type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type = type).order_by('-sales')
        else:
            skus = GoodsSKU.objects.filter(type = type).order_by('id')
        #分页处理
        paginator =Paginator(skus,1)
        # 获取数据 处理数据
        # 非数字
        try:
            page = int(page)
        except Exception as e:
            page =1

        # 数字大于
        if page > paginator.num_pages:
            page = 1

        # 获取第几页的实例
        sku_page = paginator.page(page)
        # todo: 进行页码的控制，页面上最多显示5个页码
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_page = paginator.num_pages
        # 1.总页数小于5页，页面上显示所有页码
        if num_page < 5:
            pages = range(1,num_page+1)
        # 2.如果当前页是前3页，显示1-5页
        elif page <= 3:
            pages = range(1,6)
        # 3.如果当前页是后3页，显示后5页
        elif num_page - page <= 2:
            pages = range(num_page-4,num_page+1 )

        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        else:
            pages = range(page-2, page+3)
        # 获取新品推荐
        new_skus = GoodsSKU.objects.filter(type = type).order_by('-create_time')[:2]

        # 获取购物车的数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_{0}'.format(user.id)
            cart_count = conn.hlen(cart_key)

        context = {
            'type' : type,
            'types' : types,
            'pages' : pages,
            'cart_count' : cart_count,
            'new_skus' : new_skus,
            'sort' : sort,
            'sku_page':sku_page
        }
        return render(request,'list.html',context=context)