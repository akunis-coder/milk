from django.contrib import admin  # Import the admin module from Django's built-in admin package
from django.urls import path, include   # Import path and include for URL routing
#from MilkProductstore import settings  # Import the settings from the MilkProductstore project
from django.conf import settings
from django.conf.urls.static import static  # Import static for serving media files during development

# Define the URL patterns for the project
urlpatterns = [
    # URL path for the Django admin interface
    path('admin/', admin.site.urls),  
    
    # Include URLs from the MilkProductapp application under the 'api/' route
    path('api/', include('MilkProductapp.urls')),  

]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)