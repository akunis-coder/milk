# Import necessary decorators and classes from Django REST Framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone
from .models import UserRegistration, UserProfile, SupplierCustomerRelation, Cart, CartItem, Product, Invoice, InvoiceItem, NegotiablePrice, Brand
from django.contrib.auth.models import User
from decimal import Decimal
from rest_framework import viewsets, permissions, status
from .serializers import (BrandSerializer, ProductSerializer, UserRegistrationSerializer, UserProfileSerializer, SupplierCustomerRelationSerializer, CartSerializer, CartItemSerializer, InvoiceSerializer, InvoiceItemSerializer, NegotiablePriceSerializer)
from rest_framework import viewsets,generics
from rest_framework.authtoken.models import Token
from bson.decimal128 import Decimal128
from django.core.exceptions import ObjectDoesNotExist
import logging
import re
from django.db.models import Count


logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request):
    user_registration = get_object_or_404(UserRegistration, user=request.user)  # Get the user registration
    user_profile = user_registration.userprofile  # Get the user profile
    data = {'username': user_registration.user.username,'mobile_number': user_registration.mobile_number,'alternate_number': user_registration.alternate_number,'address': user_registration.address,'shop_name': user_profile.shopName,'shop_photo': request.build_absolute_uri(user_profile.shopPhoto.url) if user_profile.shopPhoto else None,'email': user_profile.email,}
    return Response(data)

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()  # Get all brands
    serializer_class = BrandSerializer  # Use this serializer for data conversion
    def create(self, request, *args, **kwargs):  # Check if the user's mobile number matches the allowed one
        if request.user.userregistration.mobile_number != '9848098480':             
            return Response({'success': False, 'message': 'You are not authorized to add products.'}, status=status.HTTP_403_FORBIDDEN)        
        return super().create(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()  # Get all products
    serializer_class = ProductSerializer  # Use this serializer for data conversion
    def create(self, request, *args, **kwargs):  # Check if the user's mobile number matches the allowed one
        if request.user.userregistration.mobile_number != '9848098480':             
            return Response({'success': False, 'message': 'You are not authorized to add products.'}, status=status.HTTP_403_FORBIDDEN)        
        return super().create(request, *args, **kwargs)

class UserRegistrationViewSet(viewsets.ModelViewSet):
    queryset = UserRegistration.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [{"username": registration.user.username,"mobile_number": registration.mobile_number,"alternate_number": registration.alternate_number,"address": registration.address}for registration in queryset]
        return Response(data)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()  # Get all user profiles
    serializer_class = UserProfileSerializer  # Use this serializer for data conversion

class SupplierCustomerRelationViewSet(viewsets.ModelViewSet):
    queryset = SupplierCustomerRelation.objects.all()  # Get all supplier-customer relations
    serializer_class = SupplierCustomerRelationSerializer  # Use this serializer for data conversion

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()  # Get all carts
    serializer_class = CartSerializer  # Use this serializer for data conversion

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()  # Get all cart items
    serializer_class = CartItemSerializer  # Use this serializer for data conversion

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()  # Get all invoices
    serializer_class = InvoiceSerializer  # Use this serializer for data conversion

class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()  # Get all invoice items
    serializer_class = InvoiceItemSerializer  # Use this serializer for data conversion

class NegotiablePriceViewSet(viewsets.ModelViewSet):
    queryset = NegotiablePrice.objects.all()  # Get all negotiated prices
    serializer_class = NegotiablePriceSerializer  # Use this serializer for data conversion

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    mobile_number = request.data.get('mobile_number')
    alternate_number = request.data.get('alternate_number')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')
    address = request.data.get('address')
   
    # Validate that username does not contain numbers
    if any(char.isdigit() for char in username):
        return Response({'success': False, 'message': "Username must not contain numbers"}, status=400)
   
    # Validate mobile number and alternate number
    if not (mobile_number.isdigit() and len(mobile_number) == 10):
        return Response({'success': False, 'message': "Mobile number must be exactly 10 digits"}, status=400)
   
    if not (alternate_number.isdigit() and len(alternate_number) == 10):
        return Response({'success': False, 'message': "Alternate number must be exactly 10 digits"}, status=400)
 
 
    # Validate password and confirm password
    if password != confirm_password:
        return Response({'success': False, 'message': "Passwords do not match"}, status=400)
 
    # Check if mobile number is already registered
    if UserRegistration.objects.filter(mobile_number=mobile_number).exists():
        return Response({'success': False, 'message': "Mobile number already registered"}, status=400)
 
    user = User.objects.create_user(username=username, password=password)
    user_registration = UserRegistration.objects.create(user=user,mobile_number=mobile_number,alternate_number=alternate_number,address=address)
    UserProfile.objects.create(user_registration=user_registration, verification='supplier')
 
    token, created = Token.objects.get_or_create(user=user)
 
    auth_login(request, user)
    return Response({
        'success': True,
        'message': "Registration successful",
        'token': token.key,
        'data': {'username': username,'mobile_number': mobile_number,'alternate_number': alternate_number,'address': address}})
 
 

@api_view(['POST'])
def login(request):
    mobile_number = request.data.get('mobile_number')
    password = request.data.get('password')
    try:
        user_registration = UserRegistration.objects.get(mobile_number=mobile_number)
        user = authenticate(username=user_registration.user.username, password=password)
        if user is not None:
            auth_login(request, user)  # Log the user in
            user.last_login = timezone.now()  # Update last login time
            user.save()  # Save user info
            token, created = Token.objects.get_or_create(user=user)
            return Response({'success': True,'message': 'You have successfully logged in.','token': token.key})
        return Response({'success': False, 'message': 'Invalid password.'}, status=400)
    except UserRegistration.DoesNotExist:
        return Response({'success': False, 'message': 'User does not exist.'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def logout(request):
    auth_logout(request)  # Log the user out
    return Response({'success': True, 'message': 'Logged out successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request):
    try:
        user_registration = getattr(request.user, 'userregistration', None)
        if not user_registration:
            return Response({'error': 'User registration not found'}, status=404)
        user_profile = UserProfile.objects.get(user_registration=user_registration)
        user_mobile_number = user_profile.user_registration.mobile_number
        is_supplier = SupplierCustomerRelation.objects.filter(supplier_mobile_number=user_mobile_number).exists()
        is_customer = SupplierCustomerRelation.objects.filter(customer_mobile_number=user_mobile_number).exists()
        if is_supplier and is_customer:
            return Response({'redirect': 'supplier_customer_home'})
        elif is_customer:
            return Response({'redirect': 'customer_home'})
        else:
            return Response({'redirect': 'customer_home'})
 
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])  # Ensure user is authenticated
# def home(request):
#     user_profile = get_object_or_404(UserProfile, user_registration=request.user.userregistration)
#     user_mobile_number = user_profile.user_registration.mobile_number

#     is_supplier = SupplierCustomerRelation.objects.filter(supplier_mobile_number=user_mobile_number).exists()
#     is_customer = SupplierCustomerRelation.objects.filter(customer_mobile_number=user_mobile_number).exists()

#     if is_supplier and is_customer:
#         return Response({'redirect': 'supplier_customer_home'})  # Redirect to supplier_customer_home
#     elif is_supplier:
#         return Response({'redirect': 'supplier_home'})  # Redirect to supplier_home
#     elif is_customer:
#         return Response({'redirect': 'customer_home'})  # Redirect to customer_home
#     else:
#         return Response({'redirect': 'customer_home'})  # Redirect if user is not in SupplierCustomerRelation

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_home(request):
    return Response({'message': 'Welcome to the Customer Home Page!'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_customer_home(request):
    return Response({'message': 'Welcome to the Supplier-Customer Home Page!'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_home(request):
    return Response({'message': 'Welcome to the Supplier Home Page!'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def select_supplier(request):
    supplier_mobile_number = request.data.get('supplier_mobile_number')
    
    if not supplier_mobile_number:
        return HttpResponseBadRequest("Supplier mobile_number not provided")
    try:
        supplier = UserRegistration.objects.get(mobile_number=supplier_mobile_number)  # Get supplier by mobile number
        customer_registration = request.user.userregistration  # Get current user's registration
        SupplierCustomerRelation.objects.update_or_create(supplier_mobile_number=supplier.mobile_number,customer_mobile_number=customer_registration.mobile_number,defaults={'supplier_name': supplier.user.username, 'customer_name': customer_registration.user.username})
        return Response({'success': True, 'message': 'Supplier selected successfully!'})
    except UserRegistration.DoesNotExist:
        return Response({'success': False, 'message': "Supplier not found"}, status=400)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Ensure user is authenticated
# def get_suppliers(request):
#     current_user_mobile = request.user.userregistration.mobile_number  # Get current user's mobile number
#     suppliers = UserRegistration.objects.filter(userprofile__verification='supplier').exclude(mobile_number=current_user_mobile)
#     return Response({'suppliers': [supplier.mobile_number for supplier in suppliers]})

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def get_suppliers(request):
    current_user_mobile = request.user.userregistration.mobile_number  # Get current user's mobile number
 
    # Retrieve suppliers who have at least one invoice and exclude the current user
    suppliers = UserRegistration.objects.filter(userprofile__verification='supplier').exclude(mobile_number=current_user_mobile)
 
    # Filter suppliers based on their invoice count
    suppliers_with_invoices = [
        supplier for supplier in suppliers if Invoice.objects.filter(customerMobileNumber=supplier.mobile_number).exists()
    ]
 
    # Create a list of supplier mobile numbers
    supplier_numbers = [supplier.mobile_number for supplier in suppliers_with_invoices]
 
    # Include the specific supplier if they are not already in the list
    specific_supplier_mobile = '9848098480'
    if specific_supplier_mobile not in supplier_numbers:
        supplier_numbers.append(specific_supplier_mobile)
 
    # Return the response
    return Response({
        'suppliers': supplier_numbers,
        'message': 'Suppliers retrieved successfully.' if supplier_numbers else 'No suppliers found.'
    })

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Ensure user is authenticated
# def products(request):
#     user_mobile = request.user.userregistration.mobile_number  # Get current user's mobile number
#     supplier_relation = SupplierCustomerRelation.objects.filter(customer_mobile_number=user_mobile).order_by('-updated_at').first()
#     if not supplier_relation:
#         return Response({'success': False, 'message': "No supplier selected"}, status=400)
#     supplier_mobile = supplier_relation.supplier_mobile_number
#     products = Product.objects.all()
#     product_list = []
#     for product in products:
#         if isinstance(product.productPrice, Decimal128):
#             base_price = float(product.productPrice.to_decimal())  # Convert to Decimal first
#         else:
#             base_price = float(product.productPrice)  # Handle other types, if necessary
#         try:
#             relationship = SupplierCustomerRelation.objects.get(supplier_mobile_number=supplier_mobile,customer_mobile_number=user_mobile)
#             negotiated_price = NegotiablePrice.objects.filter(relationship=relationship,product__productid=product.productid).first()
#             if negotiated_price:
#                 final_price = negotiated_price.final_price
#             else:
#                 final_price = base_price
#         except SupplierCustomerRelation.DoesNotExist:
#             final_price = base_price  # Default to base price if no relationship found
#             logger.info("No relationship found between the customer and supplier.")
#         except NegotiablePrice.DoesNotExist:
#             final_price = base_price  # Default to base price if no negotiated price found
#         if isinstance(final_price, Decimal):
#             final_price = float(final_price)
#         elif hasattr(final_price, 'to_decimal'):
#             final_price = float(final_price.to_decimal())
#         logger.info(f"Final price for product {product.productid}: {final_price}")
#         brand_name = getattr(product.brandID, 'brandName', 'Unknown Brand')  # Handle missing brand
#         image_url = request.build_absolute_uri(product.productImage.url) if product.productImage else None
#         product_data = {'id': product.productid,'Final_Price': final_price,'image_url': image_url,'category': product.productCategory,'type': product.productType,'volume': product.productVolume,'description': product.productDescription,'brand': brand_name}
#         product_list.append(product_data)
#     return Response({'success': True, 'products': product_list})
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from MilkProductapp.models import Product, SupplierCustomerRelation, NegotiablePrice

from bson import Decimal128

import time
 
@api_view(['GET'])

@permission_classes([IsAuthenticated])

def products(request):

    start_time = time.time()
 
    user_mobile = request.user.userregistration.mobile_number

    supplier_relation = SupplierCustomerRelation.objects.filter(customer_mobile_number=user_mobile).order_by('-updated_at').first()

    if not supplier_relation:

        return Response({'success': False, 'message': "No supplier selected"}, status=400)

    supplier_mobile = supplier_relation.supplier_mobile_number

    # Fetch all products and related data in a single go

    products = Product.objects.prefetch_related('negotiableprice_set').select_related('brandID').all()
 
    # Fetch all relationships and negotiated prices in one query

    relationships = SupplierCustomerRelation.objects.filter(

        supplier_mobile_number=supplier_mobile,

        customer_mobile_number=user_mobile

    )

    negotiated_prices = NegotiablePrice.objects.filter(relationship__in=relationships)

    # Create a dictionary for quick lookup of negotiated prices

    negotiated_price_dict = {np.product.productid: np.final_price for np in negotiated_prices}

    product_list = []

    for product in products:

        # Efficient price calculation

        base_price = float(product.productPrice.to_decimal()) if isinstance(product.productPrice, Decimal128) else float(product.productPrice)

        final_price = negotiated_price_dict.get(product.productid, base_price)

        # Convert final_price to float if it's Decimal128

        if isinstance(final_price, Decimal128):

            final_price = float(final_price.to_decimal())

        image_url = request.build_absolute_uri(product.productImage.url) if product.productImage else None

        product_data = {

            'id': product.productid,

            'Final_Price': final_price,

            'image_url': image_url,

            'category': product.productCategory,

            'type': product.productType,

            'volume': product.productVolume,

            'description': product.productDescription,

            'brand': getattr(product.brandID, 'brandName', 'Unknown Brand')

        }

        product_list.append(product_data)

    total_duration = time.time() - start_time

    print(f"Total execution time: {total_duration:.4f} seconds")

    return Response({'success': True, 'products': product_list})

 
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Ensure user is authenticated
# def products(request):
#     user_mobile = request.user.userregistration.mobile_number  # Get current user's mobile number
#     supplier_relation = SupplierCustomerRelation.objects.filter(customer_mobile_number=user_mobile).order_by('-updated_at').first()
#     if not supplier_relation:
#         return Response({'success': False, 'message': "No supplier selected"}, status=400)
#     supplier_mobile = supplier_relation.supplier_mobile_number
#     products = Product.objects.all()
#     product_list = []
#     for product in products:
#         if isinstance(product.productPrice, Decimal128):
#             base_price = float(product.productPrice.to_decimal())  # Convert to Decimal first
#         else:
#             base_price = float(product.productPrice)  # Handle other types, if necessary
#         try:
#             relationship = SupplierCustomerRelation.objects.get(supplier_mobile_number=supplier_mobile,customer_mobile_number=user_mobile)
#             negotiated_price = NegotiablePrice.objects.filter(relationship=relationship,product__productid=product.productid).first()
#             if negotiated_price:
#                 final_price = negotiated_price.final_price
#             else:
#                 final_price = base_price
#         except SupplierCustomerRelation.DoesNotExist:
#             final_price = base_price  # Default to base price if no relationship found
#             logger.info("No relationship found between the customer and supplier.")
#         except NegotiablePrice.DoesNotExist:
#             final_price = base_price  # Default to base price if no negotiated price found
#         if isinstance(final_price, Decimal):
#             final_price = float(final_price)
#         elif hasattr(final_price, 'to_decimal'):
#             final_price = float(final_price.to_decimal())
#         logger.info(f"Final price for product {product.productid}: {final_price}")
#         brand_name = getattr(product.brandID, 'brandName', 'Unknown Brand')  # Handle missing brand
#         image_url = request.build_absolute_uri(product.productImage.url) if product.productImage else None
#         product_data = {'id': product.productid,'Final_Price': final_price,'image_url': image_url,'category': product.productCategory,'type': product.productType,'volume': product.productVolume,'description': product.productDescription,'brand': brand_name}
#         product_list.append(product_data)
#     return Response({'success': True, 'products': product_list})

# Add a product to the cart
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])  # Ensure user is authenticated
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, productid=product_id)  # Get product by ID
#     cart, _ = Cart.objects.get_or_create(user=request.user.userregistration)  # Get or create cart for the user
 
#     # Get the quantity from the request data
#     quantity = request.data.get('quantity', 1)  # Default to 1 if not provided
#     try:
#         quantity = int(quantity)  # Ensure quantity is an integer
#         if quantity <= 0:
#             return Response({'success': False, 'message': 'Quantity must be greater than 0'}, status=400)
#     except ValueError:
#         return Response({'success': False, 'message': 'Invalid quantity'}, status=400)
 
#     # Retrieve the supplier relationship
#     user_mobile = request.user.userregistration.mobile_number
#     supplier_relation = SupplierCustomerRelation.objects.filter(customer_mobile_number=user_mobile).order_by('-updated_at').first()
   
#     if not supplier_relation:
#         return Response({'success': False, 'message': "No supplier selected"}, status=400)
 
#     # Get the selected supplier's mobile number
#     supplier_mobile = supplier_relation.supplier_mobile_number
 
#     # Check if there's a negotiated price for the product for the selected supplier
#     negotiated_price_query = NegotiablePrice.objects.filter(
#         relationship__customer_mobile_number=user_mobile,
#         product=product
#     )
 
#     # Set price to use
#     if negotiated_price_query.exists():
#         negotiated_price = negotiated_price_query.first().final_price
#         price_to_use = Decimal(str(negotiated_price))  # Use negotiated price
#     else:
#         price_to_use = Decimal(str(product.productPrice))  # Use base price
 
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, productItem=product)  # Get or create cart item
 
#     # Update quantity
#     if created:
#         cart_item.quantity = quantity  # If created, set the provided quantity
#     else:
#         cart_item.quantity += quantity  # If exists, increase by the provided quantity
 
#     cart_item.price = price_to_use  # Set the price for the cart item
#     cart_item.save()  # Save the cart item
 
#     return Response({'success': True, 'message': 'Product added to cart!', 'quantity': cart_item.quantity})

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, productid=product_id)  # Get product by ID
    cart, _ = Cart.objects.get_or_create(user=request.user.userregistration)  # Get or create cart for the user
 
    # Get the quantity from the request data
    quantity = request.data.get('quantity', 1)  # Default to 1 if not provided
    try:
        quantity = int(quantity)  # Ensure quantity is an integer
        if quantity <= 0:
            return Response({'success': False, 'message': 'Quantity must be greater than 0'}, status=400)
    except ValueError:
        return Response({'success': False, 'message': 'Invalid quantity'}, status=400)
 
    # Retrieve the supplier relationship
    user_mobile = request.user.userregistration.mobile_number
    supplier_relation = SupplierCustomerRelation.objects.filter(customer_mobile_number=user_mobile).order_by('-updated_at').first()
   
    if not supplier_relation:
        return Response({'success': False, 'message': "No supplier selected"}, status=400)
 
    # Get the selected supplier's mobile number
    supplier_mobile = supplier_relation.supplier_mobile_number
 
    # Fetch relationships and negotiate prices
    relationships = SupplierCustomerRelation.objects.filter(
        supplier_mobile_number=supplier_mobile,
        customer_mobile_number=user_mobile
    )
 
    # Fetch negotiated prices for the product
    negotiated_price_query = NegotiablePrice.objects.filter(
        relationship__in=relationships,
        product=product
    ).order_by('-updated_at')  # Get the latest price
 
    # Determine the price to use
    if negotiated_price_query.exists():
        negotiated_price = negotiated_price_query.first().final_price
        price_to_use = Decimal(str(negotiated_price))  # Use negotiated price
    else:
        price_to_use = Decimal(str(product.productPrice))  # Use base price
 
    # Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, productItem=product)  # Get or create cart item
 
    # Update quantity
    if created:
        cart_item.quantity = quantity  # If created, set the provided quantity
    else:
        cart_item.quantity += quantity  # If exists, increase by the provided quantity
 
    cart_item.price = price_to_use  # Set the price for the cart item
    cart_item.save()  # Save the cart item
 
    return Response({'success': True, 'message': 'Product added to cart!', 'quantity': cart_item.quantity})

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def remove_product_from_cart(request, product_id):
    product = get_object_or_404(Product, productid=product_id)  # Get product by ID
    cart, _ = Cart.objects.get_or_create(user=request.user.userregistration)  # Get or create cart for the user    
    cart_item = CartItem.objects.filter(cart=cart, productItem=product).first()  # Find the cart item
    if cart_item:
        if isinstance(cart_item.price, Decimal128):
            cart_item.price = Decimal(cart_item.price.to_decimal())
        quantity_to_remove = request.data.get('quantity', 1)  # Default to 1 if not provided
        try:
            quantity_to_remove = int(quantity_to_remove)  # Ensure it's an integer
            if quantity_to_remove <= 0:
                return Response({'success': False, 'message': 'Quantity must be greater than 0'}, status=400)
        except ValueError:
            return Response({'success': False, 'message': 'Invalid quantity'}, status=400)
        if cart_item.quantity > quantity_to_remove:
            cart_item.quantity -= quantity_to_remove  # Reduce by specified quantity
            cart_item.save()  # Save the updated cart item
            message = f'Product quantity decreased by {quantity_to_remove}.'
        elif cart_item.quantity == quantity_to_remove:
            cart_item.delete()  # Remove the item from the cart if quantity matches
            message = 'Product removed from cart.'
        else:
            return Response({'success': False, 'message': 'Quantity exceeds items in cart.'}, status=400)
    else:
        return Response({'success': False, 'message': 'Product not found in cart.'}, status=404)
    return Response({'success': True, 'message': message})

@api_view(['DELETE'])  # Use DELETE for removing an item
@permission_classes([IsAuthenticated])
def remove_entire_product_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user.userregistration)
    cart_item = get_object_or_404(CartItem, cart=cart, productItem__productid=product_id)
    cart_item.delete()
    return Response({'success': True, 'message': 'Product removed from cart completely!'})

# View cart API
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user.userregistration)  # Get or create user's cart
    cart_items = CartItem.objects.filter(cart=cart)  # Get all items in the cart
    total_price = Decimal('0.00')  # Initialize total price
    items = []  # Initialize list of items
    for item in cart_items:
        if isinstance(item.price, Decimal128):
                item.price = Decimal(item.price.to_decimal())
        item_total = item.price * item.quantity  # Calculate total price for each item
        total_price += item_total  # Update total price
        serialized_item = CartItemSerializer(item,  context={'request': request}).data
        serialized_item['total_price'] = str(item_total)  # Add total price to serialized data
        items.append(serialized_item)
    return Response({'cart_items': items, 'total_price': (total_price)})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def replace_quantity_product_in_cart(request, product_id):
    product = get_object_or_404(Product, productid=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user.userregistration)  # Get or create user's cart
    cart_item = CartItem.objects.filter(cart=cart, productItem=product).first()  # Find the cart item
    if not cart_item:
        return Response({'success': False, 'message': 'Product not found in cart.'}, status=404)
    new_quantity = request.data.get('quantity')
    if new_quantity is None:
        return Response({'success': False, 'message': 'Quantity is required.'}, status=400)
    if isinstance(cart_item.price, Decimal128):
            cart_item.price = Decimal(cart_item.price.to_decimal())
    try:
        new_quantity = int(new_quantity)  # Convert to int, make sure it’s valid
    except ValueError:
        return Response({'success': False, 'message': 'Invalid quantity.'}, status=400)
    if new_quantity <= 0:
        cart_item.delete()  # Remove the item from the cart if quantity is 0 or less
        message = 'Product removed from cart.'
    else:
        cart_item.quantity = new_quantity  # Update the quantity
        cart_item.save()  # Save the updated cart item
        message = 'Product quantity updated successfully.'
    return Response({'success': True, 'message': message})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user.userregistration)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = Decimal('0.00')
    for item in cart_items:
        if isinstance(item.price, Decimal128):
            item.price = Decimal(item.price.to_decimal())
        total_price += item.quantity * item.price 
    payment_mode = request.data.get('payment_mode')  # Get payment mode from request 
    customer_mobile_number = request.user.userregistration.mobile_number   
    supplier_customer_relation = SupplierCustomerRelation.objects.filter(customer_mobile_number=customer_mobile_number).order_by('-updated_at').first()
    if not supplier_customer_relation:
        return Response({'success': False, 'message': 'No supplier found for the customer'}, status=400) 
    invoice = Invoice.objects.create(supplierName=supplier_customer_relation.supplier_name,supplierMobileNumber=supplier_customer_relation.supplier_mobile_number,customerName=request.user.username,customerMobileNumber=request.user.userregistration.mobile_number,price=total_price) 
    for item in cart_items:
        volume_value = item.productItem.productVolume
        numeric_volume = re.sub(r'[^\d.]+', '', volume_value)
        InvoiceItem.objects.create(invoice=invoice,productItem=item.productItem,quantity=item.quantity,volume=numeric_volume,totalPrice=item.quantity * item.price,paymentMode=payment_mode,paymentStatus='Paid',transactionId='SomeTransactionId') 
    cart_items.delete() 
    return Response({'success': True, 'invoice_id': invoice.id, 'total_price': str(total_price)})
 
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)  # Get invoice by ID
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)  # Get items for the invoice
    items = [{'product_id': item.productItem.productid, 'quantity': item.quantity, 'total_price': str(item.totalPrice)} for item in invoice_items]
    return Response({'invoice_id': invoice.id, 'items': items})

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def order_history(request):
    user_registration = request.user.userregistration  # Get current user's registration
    orders = Invoice.objects.filter(customerName=request.user.username)  # Get orders for the user
    return Response({'orders': [{'id': order.id, 'price': str(order.price)} for order in orders]})

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def manage_negotiated_prices(request):
#     current_supplier_mobile = request.user.userregistration.mobile_number
#     if request.method == 'POST':
#         logger.info('POST request received for manage_negotiated_prices.')
#         customer_id = request.data.get('customer_id')
#         product_id = request.data.get('product_id')
#         new_price = request.data.get('new_price')
#         logger.info(f'Incoming POST data: {request.data}')
#         if customer_id and product_id and new_price is not None:
#             try:
#                 selected_customer = get_object_or_404(UserRegistration, id=customer_id)
#                 logger.info(f'Selected Customer: {selected_customer}')
#                 product = get_object_or_404(Product, productid=product_id)
#                 logger.info(f'Selected Product: {product}')
#                 supplier_relation, created = SupplierCustomerRelation.objects.get_or_create(supplier_mobile_number=current_supplier_mobile,customer_mobile_number=selected_customer.mobile_number)
#                 logger.info(f'Supplier-Customer Relation: {supplier_relation}')
#                 negotiable_price, created = NegotiablePrice.objects.update_or_create(relationship=supplier_relation,product=product,defaults={'final_price': new_price})
#                 logger.info(f'NegotiablePrice created/updated: {negotiable_price} (Created: {created})')
#                 return Response({'success': True, 'message': 'Product price updated successfully.'})
#             except Exception as e:
#                 logger.error(f'Error while processing request: {e}')
#                 return Response({'error': 'Error updating price'}, status=500)
#         logger.warning('Invalid data provided: customer_id, product_id, or new_price is missing.')
#         return Response({'error': 'Invalid data provided.'}, status=400)
#     else:  # Handle GET request
#         logger.info('GET request received for manage_negotiated_prices.')
#         customer_relations = SupplierCustomerRelation.objects.filter(supplier_mobile_number=current_supplier_mobile)
#         customer_ids = customer_relations.values_list('customer_mobile_number', flat=True)
#         customers = UserRegistration.objects.filter(mobile_number__in=customer_ids)
#         products = Product.objects.all()
#         product_list = []
#         for product in products:
#             try:
#                 brand_name = product.brandID.brandName
#             except ObjectDoesNotExist:
#                 brand_name = 'Unknown Brand'  # Handle missing brand            
#             final_price = None
#             for relation in customer_relations:
#                 negotiated_price = NegotiablePrice.objects.filter(relationship=relation,product=product).first()
#                 if negotiated_price:
#                     final_price = str(negotiated_price.final_price)
#                     break
#             if final_price is None:
#                 final_price = str(product.productPrice)                                                
#             product_list.append({'id': product.productid,'final_price': final_price, 'image_url': request.build_absolute_uri(product.productImage.url) if product.productImage else None,'category': product.productCategory,'type': product.productType,'volume': product.productVolume, 'description': product.productDescription, 'brand': brand_name,})
#         logger.info('Returning customers and products as JSON.')
#         return Response({'customers': [{'id': customer.id, 'mobile_number': customer.mobile_number} for customer in customers],'products': product_list})

# 
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_negotiated_prices(request):
    current_supplier_mobile = request.user.userregistration.mobile_number

    if request.method == 'POST':
        logger.info('POST request received for manage_negotiated_prices.')
        customer_id = request.data.get('customer_id')
        product_id = request.data.get('product_id')
        new_price = request.data.get('new_price')
        logger.info(f'Incoming POST data: {request.data}')

        if customer_id and product_id and new_price is not None:
            try:
                selected_customer = get_object_or_404(UserRegistration, id=customer_id)
                product = get_object_or_404(Product, productid=product_id)

                supplier_relation, created = SupplierCustomerRelation.objects.get_or_create(
                    supplier_mobile_number=current_supplier_mobile,
                    customer_mobile_number=selected_customer.mobile_number
                )

                negotiable_price, created = NegotiablePrice.objects.update_or_create(
                    relationship=supplier_relation,
                    product=product,
                    defaults={'final_price': new_price}
                )
                logger.info(f'NegotiablePrice created/updated: {negotiable_price} (Created: {created})')
                return Response({'success': True, 'message': 'Product price updated successfully.'})
            except Exception as e:
                logger.error(f'Error while processing request: {e}')
                return Response({'error': 'Error updating price'}, status=500)

        logger.warning('Invalid data provided: customer_id, product_id, or new_price is missing.')
        return Response({'error': 'Invalid data provided.'}, status=400)

    else:  # Handle GET request
        logger.info('GET request received for manage_negotiated_prices.')
        customer_relations = SupplierCustomerRelation.objects.filter(supplier_mobile_number=current_supplier_mobile)
        customer_ids = customer_relations.values_list('customer_mobile_number', flat=True)
        customers = UserRegistration.objects.filter(mobile_number__in=customer_ids)

        # Use select_related instead of prefetch_related
        products = Product.objects.select_related('brandID').all()

        negotiated_prices = NegotiablePrice.objects.filter(
            relationship__in=customer_relations,
            product__in=products
        ).select_related('relationship', 'product')

        # Create a price map for easy lookup
        price_map = {
            f"{np.relationship.customer_mobile_number}_{np.product.productid}": str(np.final_price)
            for np in negotiated_prices
        }
        product_list = []

        for product in products:
            brand_name = product.brandID.brandName if product.brandID else 'Unknown Brand'
            final_price = price_map.get(f"{current_supplier_mobile}_{product.productid}", str(product.productPrice))

            product_list.append({
                'id': product.productid,
                'final_price': final_price,
                'image_url': request.build_absolute_uri(product.productImage.url) if product.productImage else None,
                'category': product.productCategory,
                'type': product.productType,
                'volume': product.productVolume,
                'description': product.productDescription,
                'brand': brand_name,
            })

        logger.info('Returning customers and products as JSON.')
        return Response({
            'customers': [{'id': customer.id, 'mobile_number': customer.mobile_number} for customer in customers],
            'products': product_list
        })



@api_view(['POST'])
def add_products(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def view_customer_orders(request):
    current_supplier_mobile = request.user.userregistration.mobile_number
    customer_relations = SupplierCustomerRelation.objects.filter(supplier_mobile_number=current_supplier_mobile)
    customer_ids = customer_relations.values_list('customer_mobile_number', flat=True)
    invoices = Invoice.objects.filter(customerMobileNumber__in=customer_ids)
    invoice_data = [{'id': invoice.id,'customer_name': invoice.customerName,'customer_mobile_number': invoice.customerMobileNumber,'price': str(invoice.price),'date': invoice.invoiceDate,'supplier_name': invoice.supplierName,'supplier_Number': invoice.supplierMobileNumber,}for invoice in invoices]
    return Response({'success': True,'orders': {'invoices': invoice_data}})

#################################################################################9999999990
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def add_brand(request):
    serializer = BrandSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_products_by_brand(request, brandID):
    products = Product.objects.filter(brandID=brandID)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
def update_brand(request, brandID):
    try:
        brand = Brand.objects.get(brandID=brandID)
    except Brand.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = BrandSerializer(brand, data=request.data, partial=request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['PUT', 'PATCH'])
def update_product(request, productid):
    try:
        product = Product.objects.get(productid=productid)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ProductSerializer(product, data=request.data, partial=request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_brands(request):
    brands = Brand.objects.all()
    serializer = BrandSerializer(brands, many=True,  context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def retrieve_brand(request, brandID):
    try:
        brand = Brand.objects.get(brandID=brandID)
    except Brand.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = BrandSerializer(brand,  context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def list_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def retrieve_product(request, productid):
    try:
        product = Product.objects.get(productid=productid)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, context={'request': request})
    return Response(serializer.data)

class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

# Class-Based Views for retrieving, updating, and deleting a specific brand
class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

# Class-Based Views for listing and creating products
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Class-Based Views for retrieving, updating, and deleting a specific product
class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@api_view(['GET'])
def list_products_by_brand(request, brandID):
    try:
        products = Product.objects.filter(brandID=brandID)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_brand(request, pk):
    try:
        brand = Brand.objects.get(pk=pk)
    except Brand.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    brand.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    product.delete()
    return Response(status=status.HTTP_200_OK)

class BrandDeleteView(generics.DestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
