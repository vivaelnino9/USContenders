from django.core.exceptions import PermissionDenied,ObjectDoesNotExist
from django.contrib import messages

from .models import *

def user_is_captain(function):
    def wrap(request, *args, **kwargs):
        try:
            captain = Captain.objects.get(name=request.user.username)
            return function(request, *args, **kwargs)
        except ObjectDoesNotExist:
            messages.error(request, 'The submission deadline has passed.')
            raise PermissionDenied("Custom message")
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
