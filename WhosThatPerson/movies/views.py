import os
import requests
from django.shortcuts import render, redirect 
from django.contrib import messages
from django.views import View
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

APIKEY = str(os.getenv('APIKEY'))
POSTER_KEY = str(os.getenv('POSTER_KEY'))

def home(request):
    return render(request, 'movies/home.html')




class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'movies/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='/')

        return render(request, self.template_name, {'form': form})

class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)

def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'movies/password_reset.html'
    email_template_name = 'movies/password_reset_email.html'
    subject_template_name = 'movies/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('movies-home')

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'movies/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('movies-home')

def index(request):
    
    if request.method == 'POST':

        data_URL = f'http://www.omdbapi.com/?apikey={APIKEY}'
        year = ''
        movie = request.POST['movie']
        params = {
            't':movie,
            'type':'movie',
            'y':year,
            'plot':'full'
        }

        try:
            response = requests.get(data_URL,params=params).json()
            
        except Exception as e:
            raise e
        
        Title = response['Title']
        released = response['Released']
        Rating = response['Rated']
        Runtime = response['Runtime']
        Genre = response['Genre']
        Director = response['Director']
        Writer = response['Writer']
        Actors = response['Actors']
        Plot = response['Plot']
        Id = response['imdbID']
        
        info = { 
            'Title' : Title,
            'released' : released,
            'Rating' : Rating,
            'Runtime' : Runtime, 
            'Genre' : Genre,
            'Director' : Director,
            'Writer' : Writer,
            'Actors' : Actors,
            'Plot' : Plot,
        }
        try:
            poster_info = requests.get(f'https://imdb-api.com/en/API/Posters/{POSTER_KEY}/{Id}').json()
        except Exception as e:
            raise e

        poster = poster_info['posters'][0]['link']

        info['poster']= poster
        
        return render(request, 'movies/movie.html',info)
        
    return render(request, 'movies/index.html')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='movies-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'movies/profile.html', {'user_form': user_form, 'profile_form': profile_form})


# Create your views here.
