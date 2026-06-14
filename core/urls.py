from django.urls import path
from core import views

urlpatterns = [
    path('', views.home),
    path('register', views.register),
    path('verify', views.verify),
    path('login', views.login_view),
    path('dashboard', views.dashboard),
    path('product', views.product),
]