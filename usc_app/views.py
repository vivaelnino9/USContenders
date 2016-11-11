from django.shortcuts import render
from django.http import HttpResponse
from django_tables2 import RequestConfig

from usc_app.models import *
from usc_app.table import *

def index(request):
    return render(request, 'index.html')

def roster_table(request):
    queryset = Roster.objects.all()
    table = RosterTable(queryset)
    table.order_by = 'rank'
    RequestConfig(request, paginate={
        'per_page': 38
    }).configure(table)
    return render(request, 'roster_table.html', {'table': table,})
