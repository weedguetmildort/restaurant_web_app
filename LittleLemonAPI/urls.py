from django.urls import path 
from . import views 
  
urlpatterns = [
    # User registration and token generation endpoints
    path('users', views.users),
    path('users/users/me', views.display_user),
    
    # Menu-items endpoints
    path('categories', views.CategoriesView.as_view({'get':'list', 'post':'create', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),
    path('menu-items', views.MenuItemsViewSet.as_view({'get':'list', 'post':'create', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),
    path('menu-items/<int:pk>', views.MenuItemsViewSet.as_view({'get':'retrieve', 'post':'create', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),

    # User group management endpoints
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:userId>', views.managers),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:userId>', views.delivery_crew),

    # Cart management endpoints
    path('cart/menu-items', views.CartMenuItemsViewSet.as_view({'get':'list', 'post':'create', 'delete':'destroy'})),

    # Order management endpoints
    path('orders', views.OrderViewSet.as_view({'get':'list', 'post':'create', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),
    path('orders/<int:pk>', views.OrderViewSet.as_view({'get':'retrieve', 'post':'create', 'put':'update', 'patch':'partial_update', 'delete':'destroy'})),  
]
