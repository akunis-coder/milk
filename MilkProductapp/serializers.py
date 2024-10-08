# MilkProductapp/serializers.py

# Import necessary modules from Django REST framework
from rest_framework import serializers  # Import serializers for data validation and conversion
from .models import Brand, Product, UserRegistration, UserProfile, SupplierCustomerRelation, NegotiablePrice, Cart, CartItem, Invoice, InvoiceItem  # Import the models defined in models.py

# Define a serializer for the Brand model
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the Brand model

# Define a serializer for the Product model
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the Product model

# Define a serializer for the UserRegistration model
# class UserRegistrationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserRegistration  # Specify the model to serialize
#         fields = '__all__'  # Include all fields from the UserRegistration model
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserRegistration
        fields = ['user', 'username', 'mobile_number', 'alternate_number', 'address', 'password']
# Define a serializer for the UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the UserProfile model

# Define a serializer for the SupplierCustomerRelation model
class SupplierCustomerRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCustomerRelation  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the SupplierCustomerRelation model

# Define a serializer for the NegotiablePrice model
class NegotiablePriceSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(source='product.brandID', read_only=True)

    class Meta:
        model = NegotiablePrice  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the NegotiablePrice model
# class NegotiablePriceSerializer(serializers.ModelSerializer):
#     brand = BrandSerializer(source='product.brandID', read_only=True)

#     class Meta:
#         model = NegotiablePrice
#         fields = ['id', 'final_price', 'updated_at', 'relationship', 'brand', 'product']

# Define a serializer for the Cart model
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the Cart model

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'productid',
            'productImage',
            'productCategory',
            'productType',
            'productVolume',
            'productDescription',
            'brandID'
        ]
# Define a serializer for the CartItem model
class CartItemSerializer(serializers.ModelSerializer):
    productItem = CartProductSerializer()  # Use the ProductSerializer to include product details

    class Meta:
        model = CartItem  # Specify the model to serialize
        fields = ['id', 'quantity', 'price', 'cart', 'productItem']  # Add more fields as needed

# Define a serializer for the Invoice model
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the Invoice model

# Define a serializer for the InvoiceItem model
class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem  # Specify the model to serialize
        fields = '__all__'  # Include all fields from the InvoiceItem model
