from django.urls import path
from . views import home, RegisterView, profile
from . import views


urlpatterns = [
    path('', home, name='movies-home'),
    path('register/', RegisterView.as_view(), name='movies-register'),
    path('profile/', profile, name='movies-profile'),
    path('index/', views.index, name='index'),
]