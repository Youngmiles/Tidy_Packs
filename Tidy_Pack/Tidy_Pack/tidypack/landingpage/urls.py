from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('product_landing/',views.product_landing,name='product_landing'),
    path('contact/',views.contact,name='contact'),
    path('register/',views.register,name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='user_logout'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('orders/create/', views.create_order, name='create_order'),
    path('products/', views.products, name='products'),
    path('orders/',views.orders,name='orders'),
    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('manage-orders/update/<int:order_id>/', views.update_order, name='update_order'),
    path('manage-orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage-users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('reports/', views.reports, name='reports'),
   
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('manage-products/', views.product_manage, name='product_manage'),  # Changed from create_product to manage

]

