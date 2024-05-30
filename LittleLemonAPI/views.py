from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.authtoken.models import Token
from .models import MenuItem, Category, CartMenuItem, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartMenuItemSerializer, OrderSerializer, OrderItemSerializer
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from .permissions import IsManager


class CategoriesView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsManager]
        elif self.action == 'update':
            permission_classes = [IsAuthenticated, IsManager]
        elif self.action == 'partial_update':
            permission_classes = [IsAuthenticated, IsManager]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsManager]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


# /api/menu-items DONE
# /api/menu-items/{menuItem} DONE
class MenuItemsViewSet(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['title']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsManager]
        elif self.action == 'update':
            permission_classes = [IsAuthenticated, IsManager]
        elif self.action == 'partial_update':
            permission_classes = [IsAuthenticated, IsManager]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsManager]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        category_id = request.data.get('category_id')
        if category_id and not Category.objects.filter(id=category_id).exists():
            return Response({"error": "Category does not exist and need to be created first."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


# /api/users DONE
@api_view(['POST'])
def users(request):
    # Extract user data from the request
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Check if all required fields are provided
    if not all([username, email, password]):
        return Response({"error": "Username, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if the user already exists
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the user
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    # Return a success message
    return Response({"detail": "User created successfully."}, status=status.HTTP_201_CREATED)


# /api/users/users/me/ DONE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_user(request):
    # Retrieve the currently authenticated user
    user = request.user
    
    # Return user details in the response
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    })


# /token/login/ DONE
@api_view(['POST'])
def tokens(request):
    # Get the username and password from the request data
    username = request.data.get('username')
    password = request.data.get('password')

    # Check if all required fields are provided
    if not all([username, password]):
        return Response({"error": "Username, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate the user
    user = authenticate(username=username, password=password)
    if user is not None:
        # Generate or get the existing token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)
        # Return the token in the response
        return Response({"token": token.key}, status=status.HTTP_200_OK)
    else:
        # If authentication fails, return an error response
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

# /api/groups/manager/users DONE
# /api/groups/manager/users/{userId} DONE
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, IsManager])
def managers(request, userId=None):

    if request.method == 'GET':
        # Get all users in the Manager group
        try:
            managers_group = Group.objects.get(name='Manager')
            managers = managers_group.user_set.all()
            managers_list = [{'id': manager.id, 'username': manager.username, 'email': manager.email} for manager in managers]
            return Response(managers_list, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({"error": "Manager group does not exist."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        # Assign the user in the payload to the Manager group
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            managers_group, created = Group.objects.get_or_create(name='Manager')
            user.groups.add(managers_group)
            return Response({"detail": f"User {username} added to Manager group."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        # Remove the user in the payload from the Manager group
        if userId is None:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=userId)
            username = user.username
            try:
                managers_group = Group.objects.get(name='Manager')
                if user in managers_group.user_set.all():
                    user.groups.remove(managers_group)
                    return Response({"detail": f"User {username} removed from Manager group."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "User is not in the Manager group."}, status=status.HTTP_404_NOT_FOUND)
            except Group.DoesNotExist:
                return Response({"error": "Manager group does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)


# /api/groups/delivery-crew/users DONE
# /api/groups/delivery-crew/users/{userId} DONE
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, IsManager])
def delivery_crew(request, userId=None):
    
    if request.method == 'GET':
        # Get all users in the Delivery Crew group
        try:
            delivery_crew_group = Group.objects.get(name='DeliveryCrew')
            delivery_crew = delivery_crew_group.user_set.all()
            delivery_crew_list = [{'id': delivery_crew.id, 'username': delivery_crew.username, 'email': delivery_crew.email} for delivery_crew in delivery_crew]
            return Response(delivery_crew_list, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({"error": "Delivery Crew group does not exist."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        # Assign the user in the payload to the delivery_crew group
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            delivery_crew_group, created = Group.objects.get_or_create(name='DeliveryCrew')
            user.groups.add(delivery_crew_group)
            return Response({"detail": f"User {username} added to Delivery Crew group."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        # Remove the user in the payload from the delivery_crew group
        if userId is None:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=userId)
            username = user.username
            try:
                delivery_crew_group = Group.objects.get(name='DeliveryCrew')
                if user in delivery_crew_group.user_set.all():
                    user.groups.remove(delivery_crew_group)
                    return Response({"detail": f"User {username} removed from Delivery Crew group."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "User is not in the Delivery Crew group."}, status=status.HTTP_404_NOT_FOUND)
            except Group.DoesNotExist:
                return Response({"error": "Delivery Crew group does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)


# /api/cart/menu-items
class CartMenuItemsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            user = request.user
            cart_items = CartMenuItem.objects.filter(user=user)
            serializer = CartMenuItemSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Cart does not yet exist"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        user = request.user

        menu_item_id = request.data.get('menu_item_id')
        quantity = request.data.get('quantity', 1)
        
        if not menu_item_id or not quantity:
            return Response({"error": "Menu item id and quantity required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response({"detail": "Menu item does not exist."}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartMenuItem.objects.get_or_create(user=user, menu_item=menu_item, quantity=quantity)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartMenuItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        user = request.user
        CartMenuItem.objects.filter(user=user).delete()
        return Response({"detail": "All cart items deleted."}, status=status.HTTP_204_NO_CONTENT)
    

# /api/orders DONE
# /api/orders/{orderId} DONE
class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update']:
            if self.request.user.groups.filter(name='Manager').exists():
                return [IsAuthenticated()]
            if self.request.user.groups.filter(name='DeliveryCrew').exists():
                return [IsAuthenticated()]
        if self.action in ['destroy']:
            if self.request.user.groups.filter(name='Manager').exists():
                return [IsAuthenticated()]
        return super().get_permissions()

    def list(self, request):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif user.groups.filter(name='DeliveryCrew').exists():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        user = request.user
        cart_items = CartMenuItem.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=user)
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity
            )
            order_items.append(order_item)
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.user != request.user and not request.user.groups.filter(name='Manager').exists():
            return Response({"error": "You do not have permission for this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderItemSerializer(order.items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.groups.filter(name='Manager').exists() and not request.user.groups.filter(name='DeliveryCrew').exists():
            return Response({"error": "You do not have permission for this action."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if 'delivery_crew' in data and request.user.groups.filter(name='Manager').exists():
            try:
                order.delivery_crew = User.objects.get(pk=data['delivery_crew'])
            except:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
            if not order.delivery_crew.groups.filter(name='DeliveryCrew').exists():
                return Response({"error": "User must be in Delivery Crew."}, status=status.HTTP_400_BAD_REQUEST)

        if 'status' in data:
            order.status = data['status']
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.groups.filter(name='Manager').exists():
            return Response({"error": "You do not have permission for this action."}, status=status.HTTP_403_FORBIDDEN)

        order.delete()
        return Response({"detail": "Order deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.groups.filter(name='DeliveryCrew').exists():
            order.status = request.data.get('status', order.status)
            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You do not have permission for this action."}, status=status.HTTP_403_FORBIDDEN)
        