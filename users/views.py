import platform

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordResetView as DjangoPasswordResetView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView
)
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from users.forms import UserRegisterForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Konto dla {username} zostało założone! Możesz się zalogować.')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


class PasswordResetView(DjangoPasswordResetView):
    email_template_name = "users/mail/password_reset_email.html"
    html_email_template_name = "users/mail/password_reset_email.html"


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            messages.success(request, 'Hasło zostało zmienione! Możesz się zalogować.')
        return super().post(request, *args, **kwargs)
