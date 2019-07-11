from django.conf.urls import url
from .views import CartView,showCart,updateView,DeleteView

urlpatterns = [
    url(r'^add$',CartView.as_view(),name='add'),
    url(r'^showcart$',showCart.as_view(),name='showcart'),
    url(r'^update$',updateView.as_view(),name='update'),
    url(r'^delete$',DeleteView.as_view(),name='delete'),

]