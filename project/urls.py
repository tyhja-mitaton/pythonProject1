from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('profile/', views.profile),

    path('access-rules/', views.access_rules_list),
    path('access-rules/<int:rule_id>/', views.access_rule_update),

    path('<str:element_name>/', views.mock_list),
    path('<str:element_name>/<int:obj_id>/', views.mock_detail),
]