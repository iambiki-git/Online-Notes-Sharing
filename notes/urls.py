from django.urls import path
from notes import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.signin, name='login'),
    path('register/', views.registration, name='register'),
    path('logout/', views.signout, name='logout'),
]
