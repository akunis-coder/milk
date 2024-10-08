# Import necessary modules from Django
from django.db import models  # Import models for creating database models
from django.contrib.auth.models import User  # Import User model for user authentication

# Define the Brand model
class Brand(models.Model):
    brandID = models.CharField(max_length=255, primary_key=True)  # Unique identifier for the brand
    brandName = models.CharField(max_length=255)  # Name of the brand
    brandLogo = models.ImageField(upload_to='brand_logos/',null=True,blank=True)  # Image field for the brand logo

    def __str__(self):
        return self.brandName  # String representation of the Brand instance

# Define the Product model
class Product(models.Model):
    productid = models.CharField(max_length=255, primary_key=True)  # Unique identifier for the product
    productCategory = models.CharField(max_length=255)  # Category of the product
    productType = models.CharField(max_length=255)  # Type of the product
    productImage = models.ImageField(null=True,blank=True,upload_to='product_images/')  # Image field for the product image
    productVolume = models.CharField(max_length=255)  # Volume of the product
    productPrice = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    productDescription = models.TextField()  # Description of the product
    brandID = models.ForeignKey(Brand, on_delete=models.CASCADE)  # Foreign key relation to Brand

    def __str__(self):
       return f'{self.productid} - {self.productCategory}'

# Define the UserRegistration model
class UserRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one relation with User model
    mobile_number = models.CharField(max_length=15, unique=True)  # Unique mobile number for the user
    alternate_number = models.CharField(max_length=15, blank=True, null=True)  # Optional alternate number
    address = models.TextField()  # Address of the user

    def __str__(self):
        return self.mobile_number  # String representation of the UserRegistration instance

# Define the UserProfile model
class UserProfile(models.Model):
    user_registration = models.OneToOneField(UserRegistration, on_delete=models.CASCADE)  # One-to-one relation with UserRegistration
    verification = models.CharField(max_length=20, choices=[('aadharNumber', 'Aadhar Number'),  # Verification method options
                                                             ('panNumber', 'PAN Number'),
                                                             ('voterId', 'Voter ID'),
                                                             ('supplier', 'Supplier')])  # Include 'supplier' as an option

    shopName = models.CharField(max_length=255, blank=True, null=True)  # Optional shop name
    shopPhoto = models.ImageField(upload_to='shop_photos/', blank=True, null=True)  # Optional shop photo
    email = models.EmailField()  # Email address of the user

# Define the SupplierCustomerRelation model
class SupplierCustomerRelation(models.Model):
    supplier_mobile_number = models.CharField(max_length=15)  # Mobile number of the supplier
    customer_mobile_number = models.CharField(max_length=15)  # Mobile number of the customer
    supplier_name = models.CharField(max_length=255)  # Name of the supplier
    customer_name = models.CharField(max_length=255)  # Name of the customer
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set on update

    class Meta:
        unique_together = ('supplier_mobile_number', 'customer_mobile_number')  # Ensure unique combinations

    def __str__(self):
        return f"{self.supplier_name} ({self.supplier_mobile_number}) - {self.customer_name} ({self.customer_mobile_number})"  # String representation

# Define the NegotiablePrice model
class NegotiablePrice(models.Model):
    relationship = models.ForeignKey(SupplierCustomerRelation, related_name='negotiable_prices', on_delete=models.CASCADE, null=True)  # Relationship with supplier-customer
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)  # Foreign key relation to Brand
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key relation to Product
    final_price = models.DecimalField(max_digits=10, decimal_places=2)  # Final negotiated price
    updated_at = models.DateTimeField(auto_now=True)  # This should be here

    def __str__(self):
        return f"{self.product} - {self.final_price} (Supplier: {self.relationship.supplier_name if self.relationship else 'N/A'})"  # String representation

# Define the Cart model
class Cart(models.Model):
    user = models.OneToOneField(UserRegistration, on_delete=models.CASCADE)  # One-to-one relation with UserRegistration

# Define the CartItem model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Foreign key relation to Cart
    productItem = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key relation to Product
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product in the cart
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product at the time of adding to cart

# Define the Invoice model
class Invoice(models.Model):
    supplierName = models.CharField(max_length=255)  # Name of the supplier
    supplierMobileNumber = models.CharField(max_length=255)  # Name of the supplier
    customerName = models.CharField(max_length=255)  # Name of the customer
    customerMobileNumber = models.CharField(max_length=15)  # Mobile number of the customer
    invoiceDate = models.DateField(auto_now_add=True)  # Date of invoice creation
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Total price of the invoice

# Define the InvoiceItem model
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)  # Foreign key relation to Invoice
    productItem = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key relation to Product
    quantity = models.PositiveIntegerField()  # Quantity of the product in the invoice
    volume = models.FloatField()  # Volume of the product in the invoice
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)  # Total price for this item
    paymentMode = models.CharField(max_length=50)  # Payment mode (e.g., Credit Card, Cash)
    paymentStatus = models.CharField(max_length=50)  # Status of payment (e.g., Paid, Pending)
    transactionId = models.CharField(max_length=255)  # Transaction ID for payment tracking







