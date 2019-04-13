from django.conf.urls import url
from .views import LoginView,RegisterView,ActiveView,LogoutView,SiteView,InfoView
# from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^register$',RegisterView.as_view(),name='register'),
    url(r'^login$',LoginView.as_view(),name='login'),
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),
    url(r'^logout$',LogoutView.as_view(),name='logout'),
    url(r'^site$',SiteView.as_view(),name='site'),
    url(r'^info$',InfoView.as_view(),name='info')

]