from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from .models import Topic, CompetitionEntry, TopicQuestion, UserTopicScore
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import RegisterForm
from io import BytesIO
from django.http import HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import qrcode

# Create your views here.


def index(request):
    return render(request, 'quiz_app/index.html')


class RegisterView(FormView):
    redirect_authenticated_user = True
    template_name = 'quiz_app/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('quiz_app:login')
    
    def form_valid(self, form):
        form.save()
        
        return super(RegisterView, self).form_valid(form)
    

class MyLoginView(LoginView):
    template_name = 'quiz_app/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('quiz_app:topics') 
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))
    

class MyProfile(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user_scores = UserTopicScore.objects.filter(user=request.user)
            context = {
            'user_scores': user_scores
            }
            return render(request, 'quiz_app/profile.html', context=context)
        else:
            messages.error(request,'You must login first!')
            return redirect('quiz_app:login')


class TopicView(APIView):

    def get(self, request):
        topics = Topic.objects.all()
        context = {
            'topics': topics
        }
        return render(request, 'quiz_app/topics.html', context=context)


def generate_qr_code(request, topic_id):

    if request.user.is_authenticated:
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

        return HttpResponse(stream, content_type='image/png')
    else:
        messages.error(request,'You must login first!')
        return redirect('quiz_app:login')


class QuizView(APIView):

    def get(self,request,topic_id):
        if request.user.is_authenticated:
            topic = get_object_or_404(Topic, id=topic_id)
            entry, created = CompetitionEntry.objects.get_or_create(user=request.user, topic=topic)
            if created:
                messages.success(request, "You have joined the competition!")
            questions = TopicQuestion.objects.filter(topic=topic)
            for question in questions:
                question.options = question.options.splitlines()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"competition_{topic_id}",
                {
                    'type': 'update_contestants',
                }
            )            
            context = {
                'questions': questions,
                'topic_id': topic_id,
                'topic': topic,
            }
            return render(request, 'quiz_app/quiz_questions.html', context=context)
        else:
            messages.error(self.request,'You must login first!')
            return redirect('quiz_app:login')
        

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        questions = TopicQuestion.objects.filter(topic=topic)
        score = 0

        for question in questions:
            selected_option = request.POST.get('question_' + str(question.id), None)
            if selected_option is not None:
                if selected_option == question.correct_answer:
                    score += 1

        # Save the user's score in the database (optional)
        user_score, created = UserTopicScore.objects.get_or_create(user=request.user, topic=topic)
        messages.error(request,'Your answers submitted successfully.')
        user_score.score = score
        user_score.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"competition_{topic_id}",
            {
                'type': 'update_contestants',
            }
        )            
        context = {
            'score': user_score.score,
            'topic': topic
        }
        return render(request, 'quiz_app/result.html', context=context)
