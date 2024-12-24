from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import UserProfile, QuestionPost, Option


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'nickname', 'email']
class QuestionPostForm(forms.ModelForm):
    class Meta:
        model = QuestionPost
        fields = ['title', 'full_description', 'image', 'lifetime']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text']

class VoteForm(forms.Form):
    option = forms.ModelChoiceField(queryset=Option.objects.none(), widget=forms.RadioSelect)

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option'].queryset = question.options.all()


class UserRegistrationForm(UserCreationForm):
    nickname = forms.CharField(
        max_length=30,
        required=False,
        label="Никнейм",
        widget=forms.TextInput(attrs={'placeholder': 'Введите ваш никнейм'})
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Введите ваш email'})
    )

    class Meta:
        model = User
        fields = ['nickname', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.email = self.cleaned_data.get('email')

        if commit:
            user.save()
        return user

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("Неверный email или пароль.")

        if not user.check_password(password):
            raise forms.ValidationError("Неверный email или пароль.")

        self.user = user
        return self.cleaned_data