from rango.bing_search import run_query
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime

#### HELPER FUNCTIONS ###

def decode_url(url):
    return url.replace('_',' ')

def encode_url(url):
    return url.replace(' ','_')

def get_category_list():
    category_list = Category.objects.order_by('-likes')[:5]
    for category in category_list:
        category.url = encode_url(category.name)

    return category_list


### VIEWS ###

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)    

    category_list = get_category_list()
    context_dict = {'cat_list': category_list}

    page_list = Page.objects.order_by('-views')[:5]    
    context_dict["pages"] =  page_list

    if request.session.get('last_visit'):        
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())

    else:
        request.session['visits'] = 1
        request.session['last_visit'] = str(datetime.now())       

    # Return a rendered response to send to the client.
    return render_to_response('rango/index.html', context_dict, context)



def about_page(request):
    context = RequestContext(request)
    context_dict = {}
    if request.session.get('last_visit'):
        visits = request.session.get('visits')
        context_dict['visits'] = visits

    return render_to_response('rango/about.html', context_dict, context)

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    category_list = get_category_list()
    context_dict = {'cat_list': category_list, 'category_name': category_name,'category_name_url': category_name_url}

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        pass

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    return render_to_response('rango/category.html', context_dict, context)

@login_required
def add_category(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors

    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form}, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            cat = Category.objects.get(name=category_name)
            page.category = cat
            page.views = 0
            page.save()

            return category(request, category_name_url)

        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html', 
        {'category_name_url': category_name_url,
        'category_name': category_name, 'form': form},
        context)

def register(request):
    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response('rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
        context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your rango account is disabled')
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
    return render_to_response('rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')

@login_required
def profile(request):
    context = RequestContext(request)    
    
    user = User.objects.get(username=request.user)
    try:
        userprofile = UserProfile.objects.get(user=user)
    except:
        userprofile = None
    
    return render_to_response('rango/profile.html', {'user': user, 'userprofile': userprofile}, context)

def track_url(request):
    context = RequestContext(request)

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                return HttpResponseRedirect(page.url) 
            except:
                pass       

    return HttpResponseRedirect('/rango/') 









