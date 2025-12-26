from django.urls import path
from . import views
app_name = "address"


    
urlpatterns = [
    path("add_address/", views.add_address, name='add_address'),
    path('addresses/', views.address_list, name='address_list'),  # ✅ Must exist
    path('edit_address/<int:id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:id>/', views.delete_address, name='delete_address'),
    path('address/select/<int:id>/', views.select_address, name='select_address'),

]

   
   
   
   
   
   
   
   
