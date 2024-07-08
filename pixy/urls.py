from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
   openapi.Info(
      title="Pixy API",
      default_version='v1',
      description="API documentation for Pixy project",
      terms_of_service="https://www.yourapp.com/terms/",
      contact=openapi.Contact(email="contact@yourapp.com"),
      license=openapi.License(name="KT Aivle AI 24 License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'Welcome to the Pixy API',
        'swagger': request.build_absolute_uri('swagger/'),
        'redoc': request.build_absolute_uri('redoc/'),
    })

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/user/', include('accounts.urls')),
    path('api/post/', include('post.urls')),
    path('api/product/', include('product.urls')),
    
    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # ReDoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]