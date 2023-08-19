import os
import json

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings


class SetupPageView(View):
    template_name = 'setup/config.html'

    def get(self, request):
        return render(request, self.template_name)

