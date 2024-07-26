from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.conf.urls.static import static

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
    path('api/notice/', include('notice.urls')),
    path('api/post/', include('post.urls')),
    path('api/product/', include('product.urls')),
    path('api/store/', include('store.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/fire_detection/', include('fire_detection.urls')),
    path('api/theft_detection/', include('theft_detecion.urls')),
    # path('api/pixycustom/', include('pixycustom.urls')),
    path('api/custom/', include('custom.urls')),

    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),

    # ReDoc
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
