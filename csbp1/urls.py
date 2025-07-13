"""
URL configuration for csbp1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView
import notes.views

urlpatterns = [
    # FLAW 4 - Security Misconfiguration -
    path('', notes.views.loginView, name='login'),
    path('login/', notes.views.loginView, name='login'),
    path('notes/login/', notes.views.loginView, name='login'),
    path('logout/', notes.views.logoutView, name='logout'),
    # FIX 4 - Security Misconfiguration -
    # path('', LoginView.as_view(template_name='login.html'), name='login'),
    # path('login/', LoginView.as_view(template_name='login.html' ), name='login'),
    # path('notes/login/', LoginView.as_view(template_name='login.html' ), name='login'),
    # path('logout/', LogoutView.as_view(next_page="/login" ), name='logout'),
    #
    path('notes/', include('notes.urls')),
    path('admin/', admin.site.urls),
]
