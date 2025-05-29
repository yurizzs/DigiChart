from django.urls import path
from . import views

urlpatterns = [
    path('user/add', views.add_user),
    path('user/list', views.user_list),
    path('user/edit/<int:user_id>', views.edit_user),
    path('user/delete/<int:user_id>', views.delete_user),
    path('patient/add', views.add_patient),
    path('patient/list', views.patient_list),
]