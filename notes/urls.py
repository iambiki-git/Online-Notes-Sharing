from django.urls import path
from notes import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.signin, name='login'),
    path('register/', views.registration, name='register'),
    path('logout/', views.signout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notes/', views.notes, name='note'),
    path('notification/', views.notification, name='notification'),
    path('dashboard/myprofile/', views.myprofile, name='myprofile'),
    path('dashboard/mynotes/', views.mynotes, name='mynotes'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)