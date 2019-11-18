from django.urls import path
from .views import IndexView, ProductView, ProductCreateView, BasketChangeView, BasketView, ProductUpdateView, \
    ProductDeleteView, OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderProductCreateView,\
    OrderProductDeleteView, OrderProductUpdateView, OrderDeliverView, OrderCancelView



urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('products/<int:pk>/', ProductView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('basket/change/', BasketChangeView.as_view(), name='basket_change'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('order/', OrderListView.as_view(), name='orders'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/create/', OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('order/<int:pk>/add-products/', OrderProductCreateView.as_view(), name='order_order_create'),
    path('product_delete/<int:pk>/', OrderProductDeleteView.as_view(), name='product_delete_from_order'),
    path('product_update/<int:pk>/', OrderProductUpdateView.as_view(), name='product_update_in_order'),
    path('order-deliver/<int:pk>/', OrderDeliverView.as_view(), name='order_deliver'),
    path('order-cancel/<int:pk>/', OrderCancelView.as_view(), name='order_cancel'),
]

app_name = 'webapp'