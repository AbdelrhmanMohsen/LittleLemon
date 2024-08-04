from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, User
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from .permissions import IsManager
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import NotFound
from django.contrib.auth import authenticate
from decimal import InvalidOperation, Decimal
from django.utils import timezone

# Create your views here.
#__________________________________

#Menu-items endpoints
class MenuItemList(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsAuthenticated(), IsManager()]
        else:
            return [IsAdminUser()]

class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManager()]
        else:
            return [IsAdminUser()]
#__________________________________________________________________________________________________________
#User group management endpoints  
# Managers
class ListCreateManagerUsers(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user)
            return Response({'status': 'user added to manager group'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'manager group not found'}, status=status.HTTP_404_NOT_FOUND)

class RemoveManagerUser(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.remove(user)
            return Response({'status': 'user removed from manager group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'manager group not found'}, status=status.HTTP_404_NOT_FOUND)
#_________________________________________________
#Delivery Crew
class ListCreateDeliveryCrewUsers(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery Crew')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            delivery_crew_group = Group.objects.get(name='Delivery Crew')
            delivery_crew_group.user_set.add(user)
            return Response({'status': 'user added to delivery crew group'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'delivery crew group not found'}, status=status.HTTP_404_NOT_FOUND)

class RemoveDeliveryCrewUser(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            delivery_crew_group = Group.objects.get(name='Delivery Crew')
            delivery_crew_group.user_set.remove(user)
            return Response({'status': 'user removed from delivery crew group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'delivery crew group not found'}, status=status.HTTP_404_NOT_FOUND)
        
#___________________________________________________________________________________________________________________________
        
#Cart management endpoints 
class CartManagementView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()
        queryset.delete()
        return Response({"message": f"Deleted {count} items"}, status=status.HTTP_204_NO_CONTENT) 
#______________________________________________________________________________________________________________________________

#Order management endpoints    
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.user != request.user and not self.request.user.groups.filter(name='Manager').exists():
            return Response({"detail": "Not authorized to update this order."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        if order.user != request.user and not self.request.user.groups.filter(name='Manager').exists():
            return Response({"detail": "Not authorized to delete this order."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
    
class DeliveryCrewOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show orders assigned to the delivery crew
        return Order.objects.filter(delivery_crew=self.request.user)

class DeliveryCrewOrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show orders assigned to the delivery crew
        return Order.objects.filter(delivery_crew=self.request.user)

    def update(self, request, *args, **kwargs):
        # Ensure delivery crew can only update the status
        instance = self.get_object()
        if 'status' not in request.data:
            return Response({"detail": "Status field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery_crew != request.user:
            return Response({"detail": "Not authorized to update this order."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
class AssignOrderToDeliveryCrewView(APIView):
    permission_classes = [IsAdminUser | IsManager]

    def post(self, request, order_id, user_id):
        order = Order.objects.get(id=order_id)
        delivery_crew = User.objects.get(id=user_id)
        order.delivery_crew = delivery_crew
        order.save()
        return Response({'status': 'order assigned to delivery crew'})
    
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id, delivery_crew=request.user)
        order.status = True
        order.save()
        return Response({'status': 'order marked as delivered'})
#_________________________________________________________________________________________________________________________
    
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] 
    
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser | IsManager]
    
class UpdateItemOfTheDayView(APIView):
    permission_classes = [IsAdminUser | IsManager]

    def post(self, request, menu_item_id):
        menu_item = MenuItem.objects.get(id=menu_item_id)
        menu_item.featured = True
        menu_item.save()
        return Response({'status': 'item updated as featured'})
#_______________________________________________________________________________________________________________________________
    
# class AddToCartView(generics.CreateAPIView):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
        
# class CartListView(generics.ListAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user)
    
# class PlaceOrderView(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
        
# class CustomerOrderListView(generics.ListAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user)
    
    
# class MenuItemListView(generics.ListAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     permission_classes = [AllowAny]
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     filterset_fields = ['category']
#     ordering_fields = ['price']
        
# class MenuItemCreateView(generics.CreateAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     permission_classes = [IsAdminUser]

# class AssignManagerView(APIView):
#     permission_classes = [IsAdminUser]

#     def post(self, request, user_id):
#         user = User.objects.get(id=user_id)
#         manager_group, created = Group.objects.get_or_create(name='Manager')
#         manager_group.user_set.add(user)
#         return Response({'status': 'user assigned to manager group'})

# class AssignDeliveryCrewView(generics.CreateAPIView):
#     permission_classes = [IsAdminUser | IsManager]
    
#     def post(self, request, user_id):
#         user = User.objects.get(id=user_id)
#         delivery_crew_group, created = Group.objects.get_or_create(name='Delivery Crew')
#         delivery_crew_group.user_set.add(user)
#         return Response({'status': 'user assigned to delivery crew group'})

# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]
    
# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
#         return Response({'error': 'Invalid credentials'}, status=400)

# class MenuItemViewSet(viewsets.ModelViewSet):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer

#     def get_permissions(self):
#         if self.action in ['create', 'update', 'partial_update', 'destroy']:
#             permission_classes = [IsAuthenticated, IsManager]
#         elif self.action in ['list', 'retrieve']:
#             permission_classes = []
#         else:
#             permission_classes = [IsAuthenticated]
#         return [permission() for permission in permission_classes]

# class UserGroupViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def get_group(self, group_name):
#         try:
#             return Group.objects.get(name=group_name)
#         except Group.DoesNotExist:
#             raise NotFound(detail=f'Group {group_name} not found.')

#     @action(detail=False, methods=['get'], url_path='manager/users')
#     def list_managers(self, request):
#         group = self.get_group('Manager')
#         users = group.user_set.all()
#         user_data = [{'id': user.id, 'username': user.username} for user in users]
#         return Response(user_data, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['post'], url_path='manager/users')
#     def add_manager(self, request):
#         user_id = request.data.get('user_id')
#         if not user_id:
#             return Response({'detail': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
#         group = self.get_group('Manager')
#         group.user_set.add(user)
#         return Response({'detail': 'User added to Manager group.'}, status=status.HTTP_201_CREATED)

#     @action(detail=True, methods=['delete'], url_path='manager/users/(?P<user_id>\d+)')
#     def remove_manager(self, request, user_id=None):
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
#         group = self.get_group('Manager')
#         group.user_set.remove(user)
#         return Response({'detail': 'User removed from Manager group.'}, status=status.HTTP_200_OK)
    
#     @action(detail=False, methods=['get'], url_path='delivery-crew/users')
#     def list_delivery_crew(self, request):
#         group = self.get_group('Delivery crew')
#         users = group.user_set.all()
#         user_data = [{'id': user.id, 'username': user.username} for user in users]
#         return Response(user_data, status=status.HTTP_200_OK)


#     @action(detail=False, methods=['post'], url_path='delivery-crew/users')
#     def add_delivery_crew(self, request):
#         user_id = request.data.get('user_id')
#         if not user_id:
#             return Response({'detail': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
#         group = self.get_group('Delivery crew')
#         group.user_set.add(user)
#         return Response({'detail': 'User added to Delivery crew group.'}, status=status.HTTP_201_CREATED)

#     @action(detail=True, methods=['delete'], url_path='delivery-crew/users')
#     def remove_user_from_delivery_crew(self, request, pk=None):
#         group = self.get_group('Delivery crew')
#         try:
#             user = group.user_set.get(id=pk)
#             group.user_set.remove(user)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except User.DoesNotExist:
#             return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     @action(detail=False, methods=['get'])
#     def menu_items(self, request):
#         # Return items in the cart for the current user
#         cart_items = Cart.objects.filter(user=request.user)
#         serializer = self.get_serializer(cart_items, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['post'])
#     def menu_items(self, request):
#         # Add menu item to the cart for the current user
#         menuitem_id = request.data.get('menuitem_id')
#         quantity = request.data.get('quantity')

#         try:
#             # Retrieve the MenuItem object
#             menuitem = MenuItem.objects.get(id=menuitem_id)
#         except MenuItem.DoesNotExist:
#             return Response({'error': 'MenuItem not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             # Calculate unit price and total price
#             unit_price = menuitem.price
#             total_price = unit_price * Decimal(quantity)
#         except (InvalidOperation, ValueError):
#             return Response({'error': 'Invalid price calculation'}, status=status.HTTP_400_BAD_REQUEST)

#         # Prepare data for serializer
#         data = {
#             'user': request.user.id,
#             'menuitem_id': menuitem_id,
#             'quantity': quantity,
#             'unit_price': str(unit_price),
#             'price': str(total_price)
#         }

#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#     @action(detail=False, methods=['delete'])
#     def menu_items(self, request):
#         # Delete all menu items in the cart for the current user
#         Cart.objects.filter(user=request.user).delete()
#         return Response({'message': 'All items have been removed from the cart'}, status=status.HTTP_204_NO_CONTENT)


# class CartListCreateView(generics.ListCreateAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class CartDeleteView(generics.DestroyAPIView):
#     permission_classes = [IsAuthenticated, IsCustomer]

#     def delete(self, request, *args, **kwargs):
#         Cart.objects.filter(user=self.request.user).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class CartManagementView(generics.ListCreateAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class CartDeleteAllView(generics.DestroyAPIView):
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user)

#     def delete(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         count = queryset.count()
#         queryset.delete()
#         return Response({"message": f"Deleted {count} items"}, status=status.HTTP_204_NO_CONTENT)

# class OrderViewSet(viewsets.ViewSet):
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
#             if self.request.user.groups.filter(name='Manager').exists():
#                 return [IsAdminUser()]
#             elif self.request.user.groups.filter(name='Delivery Crew').exists():
#                 return [IsAuthenticated()]
#             else:
#                 return [IsAuthenticated()]
#         return [IsAuthenticated()]

#     def list(self, request):
#         if self.request.user.groups.filter(name='Manager').exists():
#             orders = Order.objects.all()
#             serializer = OrderSerializer(orders, many=True)
#             return Response(serializer.data)
#         elif self.request.user.groups.filter(name='Delivery Crew').exists():
#             orders = Order.objects.filter(delivery_crew=self.request.user)
#             serializer = OrderSerializer(orders, many=True)
#             return Response(serializer.data)
#         else:
#             orders = Order.objects.filter(user=self.request.user)
#             serializer = OrderSerializer(orders, many=True)
#             return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         order = get_object_or_404(Order, pk=pk, user=self.request.user)
#         serializer = OrderSerializer(order)
#         return Response(serializer.data)

#     def create(self, request):
#         # Add items from cart to the new order
#         cart_items = Cart.objects.filter(user=request.user)
#         if not cart_items.exists():
#             return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

#         total = sum(item.price for item in cart_items)
#         order_data = {
#             'user': request.user.id,
#             'total': total,
#             'date': timezone.now().date()
#         }

#         serializer = OrderSerializer(data=order_data)
#         if serializer.is_valid():
#             order = serializer.save()
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     menuitem=item.menuitem,
#                     quantity=item.quantity,
#                     unit_price=item.unit_price,
#                     price=item.price
#                 )
#             cart_items.delete()  # Clear the cart after order creation
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def update(self, request, pk=None):
#         order = get_object_or_404(Order, pk=pk)
#         if request.user.groups.filter(name='Manager').exists():
#             serializer = OrderSerializer(order, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

#     def partial_update(self, request, pk=None):
#         order = get_object_or_404(Order, pk=pk)
#         if request.user.groups.filter(name='Delivery Crew').exists() and 'status' in request.data:
#             serializer = OrderSerializer(order, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

#     def destroy(self, request, pk=None):
#         order = get_object_or_404(Order, pk=pk)
#         if request.user.groups.filter(name='Manager').exists():
#             order.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)