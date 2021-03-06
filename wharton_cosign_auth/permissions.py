from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest

from functools import wraps

from wharton_cosign_auth.utilities import call_wisp_api


def wharton_permission(permissions):
    if not isinstance(permissions, list):
        permissions = [permissions]
        
    def wharton(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.META.get('REMOTE_USER') is not None:
                url = 'https://apps.wharton.upenn.edu/wisp/api/v1/adgroups/%s' % request.META.get(
                    'REMOTE_USER')
                response = call_wisp_api(url)
                # Check for empty response
                if response.get('groups'):
                    # Check if user is in the requested groups
                    permission_check = [
                        permission for permission in permissions if permission in response.get('groups')]
                    if permission_check:
                        return func(request, *args, **kwargs)
                    else:
                        raise PermissionDenied
                else:
                    # Return a bad request for no groups found
                    return HttpResponseBadRequest(
                        "No groups found for user %s" % request.META.get('REMOTE_USER'))
            else:
                raise PermissionDenied
        return wrapper
    return wharton
