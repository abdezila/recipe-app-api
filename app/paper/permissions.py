from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_staff(user) -> bool:
    return bool(user and user.is_authenticated and user.is_staff)


def is_author(user) -> bool:
    return bool(user and user.is_authenticated and getattr(user, "role", None) == "author")


class PaperPermissions(BasePermission):
    """
    Rules:
    - SAFE_METHODS (GET/HEAD/OPTIONS): allowed for everyone (you can restrict later)
    - POST (create): only author or staff
    - PUT/PATCH/DELETE: staff only (author cannot edit/delete)
    """

    def has_permission(self, request, view):
        # read-only actions
        if request.method in SAFE_METHODS:
            return True

        # create paper
        if request.method == "POST":
            return is_staff(request.user) or is_author(request.user)

        # update/delete paper
        return is_staff(request.user)

    def has_object_permission(self, request, view, obj):
        # read-only is allowed
        if request.method in SAFE_METHODS:
            return True

        # only staff can modify any paper (accept/reject/update/delete)
        return is_staff(request.user)
