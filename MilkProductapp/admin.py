# Import the admin module from Django's built-in admin package
from django.contrib import admin  

# Import the models defined in the application's models.py file
from .models import Brand, Product, UserRegistration, UserProfile, SupplierCustomerRelation, NegotiablePrice, Cart, CartItem, Invoice, InvoiceItem

# Register the Brand model with the Django admin site
admin.site.register(Brand)

# Register the Product model with the Django admin site
admin.site.register(Product)

# Register the UserRegistration model with the Django admin site
admin.site.register(UserRegistration)

# Register the UserProfile model with the Django admin site
admin.site.register(UserProfile)

# Register the SupplierCustomerRelation model with the Django admin site
admin.site.register(SupplierCustomerRelation)

# Register the NegotiablePrice model with the Django admin site
admin.site.register(NegotiablePrice)

# Register the Cart model with the Django admin site
admin.site.register(Cart)

# Register the CartItem model with the Django admin site
admin.site.register(CartItem)

# Register the Invoice model with the Django admin site
admin.site.register(Invoice)

# Register the InvoiceItem model with the Django admin site
admin.site.register(InvoiceItem)
