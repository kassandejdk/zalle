from django.urls import path
from utilisateurs.views import acceuil, user_login, user_logout, register,update_profile,choose_subscription, success,cancel

urlpatterns = [
    path('', acceuil, name='acceuil'),
    path('register', register, name='register'),
    path('login', user_login, name='login'),
    path('update_profile/', update_profile, name='update_profile'),
    path('logout', user_logout, name='logout'),
    path('choose_subscription/', choose_subscription, name='choose_subscription'),    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
]
