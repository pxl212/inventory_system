from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.product_list, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('export/products/', views.export_products_csv, name='export_products'),

    # 临时占位符
    path('products/<int:pk>/stock-adjustment/', views.stock_adjustment, name='stock_adjustment'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('stock/report/', views.stock_report, name='stock_report'),
    path('stock/movements/', views.movement_history, name='movement_history'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('export/movements/', views.export_stock_movements_csv, name='export_movements'),
    path('api/products/search/', views.api_product_search, name='api_product_search'),
    path('api/stock/quick-update/', views.api_quick_stock_update, name='api_quick_stock_update'),
]