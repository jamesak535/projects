from . import views
from django.urls import path
from .views import home, update_item, add_row, delete_item

urlpatterns  = [
    path('', views.home, name = 'home'),
    path('update-item/', update_item, name='update_item'),
    path('add-row/', add_row, name='add_row'),
    path('delete-item/', delete_item, name='delete_item'),

    path('save_bill/', views.save_bill, name='save_bill'),
    path('bill/<uuid:unique_id>/', views.bill_detail, name='bill_detail'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('toggle_item/', views.toggle_item, name='toggle_item'),
    path('logout/', views.logout_view, name='logout'),

    path('bill/<uuid:unique_id>/updates/', views.bill_updates, name='bill_updates'),
    # path('', home, name='home'),  # Root URL will redirect or create a new bill
    # path('<uuid:bill_uuid>/', home, name='home_with_uuid'),  # Access bills using UUID
    # path('update-item/', update_item, name='update_item'),
    # path('add-row/', add_row, name='add_row'),
    # path('delete-item/', delete_item, name='delete_item'),
]