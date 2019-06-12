from django.urls import path
from property.views import CreateAndListPropertyView, PropertyDetailView


urlpatterns = [
    path('', CreateAndListPropertyView.as_view(),
         name='create_and_list_property'),
    path('<slug:slug>/', PropertyDetailView.as_view(), name='single_property'),
]
