from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

# class IsCustomerOrDeliveryCrew(BasePermission):
#     def has_permission(self, request, view):
#         return not request.user.groups.exists() or request.user.groups.filter(name='Delivery Crew').exists()


