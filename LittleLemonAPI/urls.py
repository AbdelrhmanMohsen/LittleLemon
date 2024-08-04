from django.urls import path, include
from rest_framework import routers
from .views import * 

# router = routers.DefaultRouter()
# router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
# router.register(r'groups', UserGroupViewSet, basename='usergroup')
# router.register(r'cart/menu-items', CartViewSet, basename='cart')
# router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('add-category', CategoryCreateView.as_view(), name='add-category'),
    path('update-item-of-the-day/<int:menu_item_id>', UpdateItemOfTheDayView.as_view(), name='update-item-of-the-day'),
    path('assign-order/<int:order_id>/<int:user_id>', AssignOrderToDeliveryCrewView.as_view(), name='assign-order'),
    path('update-order-status/<int:order_id>', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('menu-items', MenuItemList.as_view(), name='menuitem-list'),
    path('menu-items/<int:pk>', MenuItemDetail.as_view(), name='menuitem-detail'),
    path('groups/manager/users', ListCreateManagerUsers.as_view(), name='list-create-manager-users'),
    path('groups/manager/users/<int:user_id>', RemoveManagerUser.as_view(), name='remove-manager-user'),
    path('groups/delivery-crew/users', ListCreateDeliveryCrewUsers.as_view(), name='list-create-delivery-crew-users'),
    path('groups/delivery-crew/users/<int:user_id>', RemoveDeliveryCrewUser.as_view(), name='remove-delivery-crew-user'),
    path('cart/menu-items', CartManagementView.as_view(), name='cart-management'),
    path('orders', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('delivery-crew/orders', DeliveryCrewOrderListView.as_view(), name='delivery-crew-order-list'),
    path('delivery-crew/orders/<int:pk>', DeliveryCrewOrderUpdateView.as_view(), name='delivery-crew-order-update'),
    path('categories', CategoryListView.as_view(), name='categories'),
    # path('manager/orders/<int:pk>', ManagerOrderDetailView.as_view(), name='manager-order-detail'),
    # path('cart/menu-items/delete', CartDeleteAllView.as_view(), name='cart-delete-all'),
    # path('register/', RegisterView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='login'),
    # path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    # path('cart/', CartListView.as_view(), name='cart'),
    # path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    # path('my-orders/', CustomerOrderListView.as_view(), name='my-orders'),
    # path('', include(router.urls)),
    # path('menu-items/', MenuItemListView.as_view(), name='menuitems'),
    # path('add-menuitem/', MenuItemCreateView.as_view(), name='add-menuitem'),
    # path('assign-manager/<int:user_id>/', AssignManagerView.as_view(), name='assign-manager'),
    # path('assign-delivery-crew/<int:user_id>/', AssignDeliveryCrewView.as_view(), name='assign-delivery-crew'),
]

# for route in router.urls:
#     print(route)