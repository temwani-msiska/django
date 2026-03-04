from accounts.models import ChildProfile


def get_child_from_request(request):
    token = getattr(request, 'auth', None)
    child_id = None
    if token and isinstance(token.payload, dict):
        child_id = token.payload.get('child_id')
    if child_id:
        try:
            child = ChildProfile.objects.get(id=child_id)
            request.child_profile = child
            return child
        except ChildProfile.DoesNotExist:
            return None
    return None
