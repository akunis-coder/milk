# Import necessary modules and functions from Django and Django REST Framework
from django.urls import path  # Import path for URL routing
from rest_framework.routers import DefaultRouter  # Import DefaultRouter to create RESTful routes
from .views import (  # Import views from the current application
    BrandViewSet,  # ViewSet for handling brands
    ProductViewSet,  # ViewSet for handling products
    UserRegistrationViewSet,  # ViewSet for handling user registrations
    UserProfileViewSet,  # ViewSet for handling user profiles
    SupplierCustomerRelationViewSet,  # ViewSet for handling supplier-customer relationships
    CartViewSet,  # ViewSet for handling carts
    CartItemViewSet,  # ViewSet for handling cart items
    InvoiceViewSet,  # ViewSet for handling invoices
    InvoiceItemViewSet,  # ViewSet for handling invoice items
    NegotiablePriceViewSet,  # ViewSet for handling negotiable prices
    register,  # Function for user registration
    login,  # Function for user login
    logout,  # Function for user logout
    home,  # Function for the home page
    select_supplier,  # Function for selecting a supplier
    get_suppliers,  # Function for getting a list of suppliers
    products,  # Function for listing products
    add_to_cart,  # Function for adding a product to the cart
    view_cart,  # Function for viewing the cart
    checkout,  # Function for the checkout process
    view_invoice,  # Function for viewing an invoice
    order_history,  # Function for viewing order history
    manage_negotiated_prices,  # Function for managing negotiated prices
    add_products,  # Function for adding new products
    view_customer_orders,  # Function for viewing customer orders
    customer_home,
    supplier_customer_home, user_details, remove_product_from_cart,remove_entire_product_from_cart,
    replace_quantity_product_in_cart,
     BrandViewSet,
    ProductViewSet,
    add_brand,
    add_products,
    update_brand,
    update_product,
    list_brands,
    retrieve_brand,
    list_products,
    retrieve_product,
    BrandListCreateView,
    BrandRetrieveUpdateDestroyView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    BrandDeleteView,
    ProductDeleteView,
    delete_brand,
    delete_product, list_brands, list_products_by_brand, supplier_home
  
)
from django.conf import settings
from django.conf.urls.static import static


# Create a router instance for registering viewsets
router = DefaultRouter()

# Register viewsets with the router
router.register(r'brands', BrandViewSet)  # Route for brands
router.register(r'products', ProductViewSet)  # Route for products
router.register(r'user-registrations', UserRegistrationViewSet)  # Route for user registrations
router.register(r'user-profiles', UserProfileViewSet)  # Route for user profiles
router.register(r'supplier-customer-relations', SupplierCustomerRelationViewSet)  # Route for supplier-customer relations
router.register(r'carts', CartViewSet)  # Route for carts
router.register(r'cart-items', CartItemViewSet)  # Route for cart items
router.register(r'invoices', InvoiceViewSet)  # Route for invoices
router.register(r'invoice-items', InvoiceItemViewSet)  # Route for invoice items
router.register(r'negotiable-prices', NegotiablePriceViewSet)  # Route for negotiable prices

# Define URL patterns for the application
urlpatterns = [
    path('register/', register, name='register'),  # URL for user registration
    path('login/', login, name='login'),  # URL for user login
    path('logout/', logout, name='logout'),  # URL for user logout
    path('home/', home, name='home'),  # URL for home page
    path('select-supplier/', select_supplier, name='select_supplier'),  # URL for selecting a supplier
    path('get-suppliers/', get_suppliers, name='get_suppliers'),  # URL for retrieving suppliers
    path('productslist/', products, name='products'),  # URL for listing products
    path('add-to-cart/<str:product_id>/', add_to_cart, name='add_to_cart'),  # URL for adding a product to the cart
    path('remove-from-cart/<str:product_id>/', remove_product_from_cart, name='remove_from_cart'),
    path('view-cart/', view_cart, name='view_cart'),  # URL for viewing the cart
    path('checkout/', checkout, name='checkout'),  # URL for the checkout process
    path('view-invoice/<int:invoice_id>/', view_invoice, name='view_invoice'),  # URL for viewing an invoice
    path('order-history/', order_history, name='order_history'),  # URL for viewing order history
    path('view-customer-orders/', view_customer_orders, name='view_customer_orders'),  # URL for viewing customer orders
    path('manage-negotiated-prices/', manage_negotiated_prices, name='manage_negotiated_prices'),  # URL for managing negotiated prices
    path('customer-home/', customer_home, name='customer_home'),
    path('supplier-customer-home/', supplier_customer_home, name='supplier_customer_home'),
    path('supplier-home/', supplier_home, name='supplier_home'),
    path('user/details/', user_details, name='user_details'),  # Add this line
    path('remove-entire-from-cart/<str:product_id>/', remove_entire_product_from_cart, name='remove_entire_product_from_cart'),
    path('replace-quantity/<str:product_id>/', replace_quantity_product_in_cart, name='replace_quantity_product_in_cart'),


# three pages urls
    path('brandslist/', list_brands, name='list-brands'),
    path('brands/<str:brandID>/', retrieve_brand, name='retrieve-brand'),
    path('products/<str:productid>/', retrieve_product, name='retrieve-product'),
    path('brands/add/', add_brand, name='add-brand'),
    path('products/add/', add_products, name='add-products'),
    path('brands/<str:brandID>/update/', update_brand, name='update-brand'),
    path('products/<str:productid>/update/', update_product, name='update-product'),
    path('brands/<str:brandID>/delete/', delete_brand, name='delete-brand'),
    path('products/<str:productid>/delete/', delete_product, name='delete-product'),
    path('products/brand/<str:brandID>/', list_products_by_brand, name='list_products_by_brand'),
    path('brands/<str:brandID>/delete/', BrandDeleteView.as_view(), name='brand-delete'),
    path('products/<str:productid>/delete/', ProductDeleteView.as_view(), name='product-delete'),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Include the router's URLs in the urlpatterns
urlpatterns += router.urls

