from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home-page'),
    path('history/', views.history, name='history'),
    path('beta/', views.beta, name='beta')
]
