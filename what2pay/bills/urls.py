from . import views
from django.urls import path
from .views import home, update_item, add_row, delete_item

urlpatterns  = [
    path('', views.home, name = 'home'),
    path('update-item/', update_item, name='update_item'),
    path('add-row/', add_row, name='add_row'),
    path('delete-item/', delete_item, name='delete_item'),

    # path('', home, name='home'),  # Root URL will redirect or create a new bill
    # path('<uuid:bill_uuid>/', home, name='home_with_uuid'),  # Access bills using UUID
    # path('update-item/', update_item, name='update_item'),
    # path('add-row/', add_row, name='add_row'),
    # path('delete-item/', delete_item, name='delete_item'),
]