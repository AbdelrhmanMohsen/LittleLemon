from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.utils import timezone

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category',
        write_only=True
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem_id', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'unit_price': {'read_only': True},
            'price': {'read_only': True}
        }

    def create(self, validated_data):
        menuitem_id = validated_data.pop('menuitem_id')
        print(f"MenuItem ID received: {menuitem_id} (Type: {type(menuitem_id)})")  # Debug output

        if isinstance(menuitem_id, int):
            menuitem = MenuItem.objects.get(id=menuitem_id)
        else:
            raise ValueError("menuitem_id must be an integer")

        unit_price = menuitem.price
        quantity = validated_data.get('quantity', 1)
        price = unit_price * quantity
        
        validated_data['menuitem'] = menuitem
        validated_data['unit_price'] = unit_price
        validated_data['price'] = price

        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        source='menuitem',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'unit_price': {'read_only': True},
            'price': {'read_only': True}
        }

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['date', 'total', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['date'] = timezone.now()

        # Get cart items
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty.")

        total = sum(item.price for item in cart_items)

        # Create the order
        order = super().create(validated_data)
        order.total = total
        order.save()

        # Add order items
        for item in cart_items:
            # Check if the item already exists for this order
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                menuitem=item.menuitem,
                defaults={
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'price': item.price
                }
            )

        # Clear the cart
        cart_items.delete()

        return order




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
