from django.conf.urls import url
from .views import userOrderView,orerdCommitView,orderPayView,CheckPayView,commentView


urlpatterns=[
    url(r'^user_order',userOrderView.as_view(),name='place'),
    url(r'^commit',orerdCommitView.as_view(),name='commit'),
    url(r'^pay',orderPayView.as_view(),name='pay'),
    url(r'^check',CheckPayView.as_view(),name='check'),
    url(r'^comment/(?P<order_id>\d+)',commentView.as_view(),name='comment')
]