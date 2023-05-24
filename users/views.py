import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordResetView as DjangoPasswordResetView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView
)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from users.forms import UserRegisterForm
from users.models import User


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


class Profile(LoginRequiredMixin, UpdateView):
    template_name = "users/profile.html"
    model = User
    fields = ["username", "email", "image"]

    def get(self, request, *args, **kwargs):
        self.kwargs[self.pk_url_kwarg] = self.request.user.pk
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(klass=self.model, pk=self.request.user.pk)
        old_image = user.image
        self.kwargs[self.pk_url_kwarg] = user.pk
        post = super().post(request, *args, **kwargs)
        if get_object_or_404(klass=self.model, pk=self.request.user.pk).image != old_image and \
                os.path.exists(old_image.path) and \
                "default_profile_image.jpg" not in old_image.path:
            os.remove(old_image.path)
        return post

    def get_success_url(self):
        return reverse_lazy("profile")
