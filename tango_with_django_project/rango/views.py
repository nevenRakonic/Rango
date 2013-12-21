from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page

#### HELPER FUNCTIONS ###

def decode_url(url):
    return url.replace('_',' ')

def encode_url(url):
    return url.replace(' ','_')

### VIEWS ###

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)

    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    for category in category_list:
        category.url = encode_url(category.name)

    page_list = Page.objects.order_by('-views')[:5]    
    context_dict["pages"] =  page_list

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('rango/index.html', context_dict, context)

def about_page(request):
    context = RequestContext(request)
    return render_to_response('rango/about.html', context)

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    context_dict = {'category_name': category_name}

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        pass

    return render_to_response('rango/category.html', context_dict, context)


