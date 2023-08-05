from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'quiz_app'

topic_patterns = [
    path("create-question/", views.CreateQuestionsView.as_view(), name="create-question"),
    path("quiz/", views.QuizView.as_view(), name="quiz_question"),
    path("result/", views.QuizView.as_view(), name="result"),
]

room_patterns = [
    path("", views.ExploreRoomView.as_view(), name="room"),
    path("create-topic/", views.CreateTopicView.as_view(), name="create-topic"),
    path("<str:topic>/", include(topic_patterns)),
]

account_patterns = [
    path("profile/", views.MyProfileView.as_view(), name='profile'),
    path('login/', views.MyLoginView.as_view(),name='login'),
    path('logout/', LogoutView.as_view(next_page='quiz_app:login'),name='logout'),
    path('register/', views.RegisterView.as_view(),name='register'),
]

urlpatterns = [
    path("", views.IndexView.as_view(), name='index'),
    path("accounts/", include(account_patterns)),
    path("all-rooms/", views.AllRoomView.as_view(), name="all-rooms"),
    path("create-room/", views.CreateRoomView.as_view(), name="create-room"),
    path("<str:room_name>/", include(room_patterns)),
]