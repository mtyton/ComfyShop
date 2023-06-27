from django.shortcuts import redirect
import os


class CheckSetupMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not os.path.exists('config.json') and not request.path_info.startswith('/setup'):
            return redirect('/setup/')

        if os.path.exists('config.json') and request.path_info.startswith('/setup'):
            return redirect('/')
        response = self.get_response(request)
        return response
