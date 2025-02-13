from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from datetime import datetime

# Create your views here.
def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    # Handle the `session` to track the access time
    visitor_cookie_handler(request)

    context_dict = {
        'boldmessage': "hey there partner!",
        'categories': category_list,
        'pages': page_list
    }
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    visitor_cookie_handler(request)
    visits = request.session.get('visits', 1)

    context_dict = {'visits': visits}
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
        context_dict['error_message'] = "The specified category does not exist."

    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        return redirect(reverse('rango:index'))

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.save()
            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
    else:
        form = PageForm()

    return render(request, 'rango/add_page.html', {'form': form, 'category': category})

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect(reverse('rango:index'))
        else:
            return render(request, 'rango/login.html', {'error': 'Invalid login details.'})

    return render(request, 'rango/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

@login_required
def restricted(request):
    """ Restricted page, accessible only to logged-in users. """
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
    return render(request, 'rango/restricted.html')

def visitor_cookie_handler(request):
   
    # Retrieve `last_visit`, if it does not exist, the default value will be `now()`.
    last_visit = request.session.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit, "%Y-%m-%d %H:%M:%S.%f")

    # Obtain `visits`, if it does not exist, the default value will be 1.
    visits = request.session.get('visits', 1)

    # The visit count will be incremented only when `last_visit` has elapsed for more than one day.
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())

    request.session['visits'] = visits