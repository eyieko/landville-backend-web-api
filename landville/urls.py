"""landville URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.views.generic.base import RedirectView

schema_view = get_schema_view(
    openapi.Info(
        title="Landville",
        default_version='v1',
        description="landVille is a simple mobile-enabled solution that helps \
      people access real estate investing with ease and convenience.\
      landVille provides users and investors with an intelligent and \
      most predictive search tool for properties in Nigeria, access to \
      saving models and financing, smart contract and documentation \
      and Our technology has four basic value proposition: search \
      capability for safe and most trusted trending properties, \
      saving and access to financing, smart contract and \
      documentation, credit rating tool",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="thelandville@gmail.com"),
    ),
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/documentation/', schema_view.with_ui('swagger', cache_timeout=0),
         name='api_documentation'),
    path('', RedirectView.as_view(url='api/documentation/', permanent=False),
         name='api_documentation'),
    path('auth/', include(("authentication.urls", "auth"), namespace="auth")),
]
