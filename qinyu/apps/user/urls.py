from django.conf.urls import url
from .views import LoginView,RegisterView,ActiveView
# from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^register$',RegisterView.as_view(),name='register'),
    url(r'^login$',LoginView.as_view(),name='login'),
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active')

]