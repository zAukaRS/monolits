from django.conf.urls.static import static
from django.urls import path
from . import views

from django.conf import settings



urlpatterns = [
    path('', views.home, name='home'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('vote/<int:question_id>/', views.vote, name='vote'),
    path('results/<int:question_id>/', views.results, name='results'),
    path('question/<int:pk>/results/', views.results, name='results'),
    path('question/create/', views.create_question, name='create_question'),
    path('register/', views.register, name='register'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('login/',  views.custom_login, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
