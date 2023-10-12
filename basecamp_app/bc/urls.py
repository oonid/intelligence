from django.urls import path

from . import views

urlpatterns = [
    path('', views.basecamp_main, name='bc-main'),
    path('auth', views.basecamp_auth, name='bc-auth'),
    path('redirect', views.basecamp_redirect, name='bc-redirect'),
    # people
    path('people/', views.app_people_main, name='app-people'),
]
