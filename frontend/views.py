from django.shortcuts import render
# from 

# Create your views here.
def index(request):
    return render(request, 'frontend/list.html')