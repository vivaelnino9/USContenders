from django.shortcuts import render
from django.http import HttpResponse

from usc_app.models import *

def index(request):
    return render(request, 'index.html')

def rosters_list(request):
    queryset = Rosters.objects.all()
    table = RostersTable(queryset)
    return render(request, 'rosters_list.html', {'table': table})
