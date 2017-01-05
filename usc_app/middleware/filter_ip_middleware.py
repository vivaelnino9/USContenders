from notify.models import Notification

class FilterIPMiddleware(object):
    def process_request(self, request):
        # number = request.user.notifications.read().count()
        return None
