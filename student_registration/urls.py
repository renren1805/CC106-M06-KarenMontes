from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from home import views
from registration import views as registration_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    path('', views.landing, name='landing'),
    path('home/', registration_views.staff_dashboard, name='home'),
    path('registration/', include('registration.urls')),
]