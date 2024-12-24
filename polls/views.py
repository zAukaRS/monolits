from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import F, Sum
from django.forms import inlineformset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .forms import UserProfileForm, QuestionPostForm, UserRegistrationForm, EmailAuthenticationForm, VoteForm, \
    OptionForm
from .models import QuestionPost, Option, UserVote, UserProfile


def home(request):
    questions = QuestionPost.objects.all()
    return render(request, 'polls/home.html', {'questions': questions})

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect('home')
        else:
            messages.error(request, "Произошла ошибка при сохранении профиля.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'polls/edit_profile.html', {'form': form})
def question_detail(request, pk):
    question = get_object_or_404(QuestionPost, pk=pk)
    if not question.is_active and not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':
        form = VoteForm(question, request.POST)
        if form.is_valid():
            selected_option = form.cleaned_data['option']
            UserVote.objects.create(user=request.user, question=question, option=selected_option)
            selected_option.votes += 1
            selected_option.save()
            return redirect('results', pk=question.pk)
    else:
        form = VoteForm(question)

    return render(request, 'polls/question_detail.html', {'question': question, 'form': form})

def results(request, pk):
    question = get_object_or_404(QuestionPost, pk=pk)
    options = question.options.all()
    total_votes = options.aggregate(total=Sum('votes'))['total'] or 0
    for option in options:
        option.percentage = (option.votes / total_votes * 100) if total_votes > 0 else 0

    return render(request, 'polls/results.html', {'question': question, 'options': options})

OptionFormSet = inlineformset_factory(
    QuestionPost,
    Option,
    form=OptionForm,
    extra=3,
    can_delete=True
)

@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionPostForm(request.POST, request.FILES)
        option_formset = OptionFormSet(request.POST)

        if form.is_valid() and option_formset.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            options = option_formset.save(commit=False)
            for option in options:
                option.question = question
                option.save()

            return redirect('home')
    else:
        form = QuestionPostForm()
        option_formset = OptionFormSet()

    return render(request, 'polls/create_question.html', {
        'form': form,
        'option_formset': option_formset
    })

@login_required
def delete_profile(request):
    user = request.user
    user.delete()
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            nickname = form.cleaned_data.get('nickname')
            if nickname:
                user.nickname = nickname
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Неверный email или пароль.")
        else:
            form.add_error(None, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = EmailAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def vote(request, question_id):
    question = get_object_or_404(QuestionPost, pk=question_id)

    if not question.is_active:
        return HttpResponseForbidden("Голосование закрыто.")

    if request.method == 'POST':
        form = VoteForm(question, request.POST)
        if form.is_valid():
            selected_option = form.cleaned_data['option']
            selected_option.votes += 1
            selected_option.save()
            return redirect('home')
    else:
        form = VoteForm(question)

    return render(request, 'polls/vote.html', {
        'question': question,
        'form': form,
    })

def results(request, question_id):
    question = get_object_or_404(QuestionPost, id=question_id)
    return render(request, 'polls/results.html', {'question': question})


@login_required
def vote(request, question_id):
    question = get_object_or_404(QuestionPost, pk=question_id)

    if not question.is_active:
        messages.error(request, "Голосование для этого вопроса закрыто.")
        return redirect('results', question_id=question.id)

    user_has_voted = UserVote.objects.filter(user=request.user, question=question).exists()

    if request.method == 'POST':
        form = VoteForm(question, request.POST)
        if form.is_valid():
            selected_option = form.cleaned_data['option']

            if user_has_voted:
                messages.warning(request, "Вы уже проголосовали за этот вопрос.")
                return redirect('results', question_id=question.id)

            try:
                UserVote.objects.create(user=request.user, question=question, option=selected_option)
                selected_option.votes += 1
                selected_option.save()
                messages.success(request, "Ваш голос учтен.")
            except IntegrityError:
                messages.error(request, "Произошла ошибка. Попробуйте снова.")
            return redirect('results', question_id=question.id)
        else:
            messages.error(request, "Произошла ошибка при обработке формы. Попробуйте ещё раз.")
    else:
        form = VoteForm(question)

    return render(request, 'polls/vote.html', {
        'question': question,
        'form': form,
        'user_has_voted': user_has_voted,
    })



@login_required
def results(request, question_id):
    question = get_object_or_404(QuestionPost, pk=question_id)
    total_votes = question.options.aggregate(total=Sum('votes'))['total'] or 0
    options = question.options.annotate(
        percentage=F('votes') * 100.0 / total_votes if total_votes > 0 else 0
    )

    return render(request, 'polls/results.html', {
        'question': question,
        'options': options,
        'total_votes': total_votes,
    })
