from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.views.generic import FormView

from .forms import CreationForm


class SignUp(FormView):
    form_class = CreationForm
    success_url = reverse_lazy("avatar_change")
    template_name = "users/signup.html"

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super(SignUp, self).form_valid(form)
