from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.http import HttpResponse
from rest_framework.views import APIView
from .models import Topic, TopicQuestion, UserTopicScore, Room
from .forms import RegisterForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from contextlib import contextmanager
from io import BytesIO
import qrcode

# Create your views here.

class UserAuthMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must log in first.')
            request.session['next_url'] = request.get_full_path()
            return redirect('quiz_app:login')
        return super().dispatch(request, *args, **kwargs)
    

@contextmanager
def generate_qr_code(request, topic_id):

    qr = qrcode.QRCode(
        version=5, 
        error_correction=qrcode.ERROR_CORRECT_H, 
        box_size=10, 
        border=5
    )
    url = request.build_absolute_uri(f"/questions/{topic_id}/")
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000000", back_color="#FFFFFF")
    stream = BytesIO()
    img.save(stream, "PNG")
    stream.seek(0)

    yield stream


class IndexView(APIView):

    def get(self, request):
        return render(request, 'quiz_app/index.html')


class RegisterView(FormView):
    redirect_authenticated_user = True
    template_name = 'quiz_app/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('quiz_app:login')
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

class MyLoginView(LoginView):
    template_name = 'quiz_app/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.session.get('next_url')
        if next_url:
            self.request.session.pop('next_url', None)
            return next_url
        else:
            return reverse_lazy('quiz_app:all-rooms')
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return super().form_invalid(form)
    

class MyProfileView(UserAuthMixin, APIView):
    
    def get(self, request):
            user_scores = UserTopicScore.objects.filter(user=request.user)
            context = {
            'user_scores': user_scores
            }
            return render(request, 'quiz_app/profile.html', context=context)


class AllRoomView(APIView):

    def get(self,request):
        rooms = Room.objects.all()
        return render(request, 'quiz_app/all_rooms.html', {'rooms':rooms})    
        

class ExploreRoomView(APIView):

    def get(self, request, room_name):
        room = get_object_or_404(Room, name=room_name)
        room_topics = Topic.objects.filter(room=room)
        return render(request, 'quiz_app/topics.html', {'topics': room_topics, 'room': room})
    

class CreateRoomView(UserAuthMixin, APIView):
    
    def get(self,request):
        user_rooms = Room.objects.user_rooms(request.user)
        return render(request, 'quiz_app/add_room.html', {'rooms':user_rooms})

    def post(self, request):
        room_name = request.POST.get('room_name').capitalize()
        user_rooms = Room.objects.user_rooms(request.user)
        rooms_name = [room.name.capitalize() for room in user_rooms]
        if room_name not in rooms_name:
            Room.objects.create(name=room_name, user=request.user)
            return redirect('quiz_app:create-topic', room_name=room_name)
        else:
            messages.warning(self.request,f"Room {room_name} already exists in your rooms.")
            return render(request, 'quiz_app/add_room.html', {'rooms':user_rooms})


class CreateTopicView(APIView):
    
    def get(self, request, room_name):
        room = get_object_or_404(Room, name=room_name)
        if request.user == room.user:
            room_topics = Topic.objects.filter(room=room)
            return render(request, 'quiz_app/add_topic.html', {'room': room, 'topics': room_topics})
        else:
            messages.warning(self.request,'You are only allowed to create topics in your room.')
            return redirect('quiz_app:all-rooms')

    def post(self, request, room_name):
        topic_name = request.POST.get('topic_name').capitalize()
        room_obj = get_object_or_404(Room, name=room_name)
        room_topics = Topic.objects.filter(room=room_obj)
        topics_name = [topic.topic.capitalize() for topic in room_topics]
        # check whether the topic name is unique or not
        if topic_name not in topics_name:
            Topic.objects.create(topic=topic_name,room=room_obj)
        else:
            messages.warning(self.request,f"Topic {topic_name} already exists in {room_name}.")
        return redirect('quiz_app:room', room_name=room_obj.name)
        

class CreateQuestionsView(APIView):

    def get(self, request, room_name, topic):
        room = get_object_or_404(Room, name=room_name)
        topic = get_object_or_404(Topic, topic=topic, room=room)
        context = {
            'topic': topic,
            'room': room_name
        }
        return render(request, 'quiz_app/add_questions.html', context=context)


    def post(self, request, room_name, topic):
        room = get_object_or_404(Room, name=room_name)
        topic = get_object_or_404(Topic, topic=topic, room=room)


class QuizView(UserAuthMixin, APIView):

    def get(self, request, room_name, topic):
        room = get_object_or_404(Room, name=room_name)
        topic = get_object_or_404(Topic, topic=topic, room=room)
        questions = TopicQuestion.objects.filter(topic=topic)
        if questions:
            entry, created = UserTopicScore.objects.get_or_create(user=request.user, topic=topic) 
            if created:
                messages.success(request, "You have joined the competition!")
            elif entry.score != 0:
                messages.info(request, f"You have already attempted {topic} quiz. Please see your score in below table.")
                return redirect('quiz_app:profile')
            for question in questions:
                question.options = question.options.splitlines()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"competition_{topic.id}",
                {
                    'type': 'update_contestants',
                }
            )            
        context = {
            'questions': questions,
            'topic': topic,
            'room': room_name
        }
        return render(request, 'quiz_app/quiz_questions.html', context=context)
        

    def post(self, request, room_name, topic):
        room = get_object_or_404(Room, name=room_name)
        topic = get_object_or_404(Topic, topic=topic, room=room)
        questions = TopicQuestion.objects.filter(topic=topic)
        score = 0

        for question in questions:
            selected_option = request.POST.get('question_' + str(question.id), None)
            if selected_option == question.correct_answer:
                score += 1

        user_score = UserTopicScore.objects.get(user=request.user, topic=topic)
        user_score.score = score
        user_score.save()
        messages.error(request,'Your answers submitted successfully.')
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"competition_{topic.id}",
            {
                'type': 'update_contestants',
            }
        )            
        context = {
            'score': user_score.score,
            'topic': topic,
            'room': room_name
        }
        return render(request, 'quiz_app/result.html', context=context)
