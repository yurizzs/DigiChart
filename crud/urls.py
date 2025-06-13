from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page),
    path('user/add/', views.add_user),
    path('user/list/', views.user_list),
    path('user/edit/<int:user_id>/', views.edit_user),
    path('user/delete/<int:user_id>/', views.delete_user),
    path('user/changepass/<int:user_id>/', views.changepass),
    path('patient/add/', views.add_patient),
    path('patient/list/', views.patient_list),
    path('patient/edit/<int:patient_id>/', views.edit_patient),
    path('patient/information/<int:patient_id>/', views.show_information),
    path('vitals/add/', views.add_vitals),
    path('vitals/info/<int:patient_id>/', views.patient_vitals),
    path('nurse/dashboard/', views.nurse_dashboard),
    path('admin/dashboard/', views.admin_dashboard),
    path('doctor/dashboard/', views.doctor_dashboard),
    path('chatbot/query/', views.chatbot_query),
    path('login/nurse/', views.nurse_login),
    path('login/admin/', views.admin_login),
    path('login/doctor/', views.doctor_login),
    path('logout/', views.logout_view),
    path('home/', views.home_page),
]