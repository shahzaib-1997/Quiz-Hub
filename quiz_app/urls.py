from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'quiz_app'

urlpatterns = [
    path("", views.index, name='index'),
    path("profile/", views.MyProfile.as_view(), name='profile'),
    path('login/', views.MyLoginView.as_view(redirect_authenticated_user=True),name='login'),
    path('logout/', LogoutView.as_view(next_page='quiz_app:login'),name='logout'),
    path('register/', views.RegisterView.as_view(redirect_authenticated_user=True),name='register'),
    path("topics/", views.TopicView.as_view(), name="topics"),
    path('topics/<int:topic_id>/', views.generate_qr_code, name='topic_qr_code'),
    path("questions/<int:topic_id>/", views.QuizView.as_view(), name="quiz_question"),
]