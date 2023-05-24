from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView
from django.urls import path
from users.views import register, PasswordResetView, PasswordResetConfirmView, Profile


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/',
         PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset-done',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset.html'),
         name='password_reset_confirm'),
    path("profile/", Profile.as_view(), name="profile"),
]
