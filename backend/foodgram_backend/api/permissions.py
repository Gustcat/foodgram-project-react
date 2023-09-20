from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """
    Permission class that grants only the author the right to change objects.
    """
    def has_permission(self, request, view):
        """
        Allows all users to view the list of objects,
        to create an object - only to an authenticated user.

        Args:
            request (HttpRequest): The request object.
            view (View): The view to which the check is applied.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Allows all users to view object details,
        to modify and delete the object - only to the author.
        Args:
        request (HttpRequest): The request object.
        view (View): The view to which the check is applied.
        obj: The object on which the action is performed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if view.action == 'retrieve':
            return True
        return obj.author == request.user
