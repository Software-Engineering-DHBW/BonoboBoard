# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    for entry in dualis_entries:
        try:
            if(entry["grade"] is not None):
                entry["grade"] = int(entry["grade"])
                entry["grade"] = entry["grade"]/10
        except ValueError:
            entry["grade"] = "Not yet set"
        try:
            if(entry["credits"] is not None):
                entry["credits"] = int(entry["credits"])
                entry["credits"] = entry["credits"]/10
        except ValueError:
            entry["grade"] = "Not yet set"

    html_template = loader.get_template('home/index.html')
    # return HttpResponse(html_template.render(content, request))
    return render(request, 'home/index.html', {"content": dualis_entries})


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


dualis_entries = [
    {'modul': 'T3INF1001', 'subject': 'Mathematik I', 'grade': '23',
        'credits': '80', 'status': None, 'date': None},
    {'modul': 'T3INF1002', 'subject': 'Theoretische Informatik I',
        'grade': '27', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF1003', 'subject': 'Theoretische Informatik II',
        'grade': '15', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF1004', 'subject': 'Programmieren', 'grade': '11',
        'credits': '90', 'status': None, 'date': None},
    {'modul': 'T3INF1005', 'subject': 'SchlÃ¼sselqualifikationen',
        'grade': '15', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF1006', 'subject': 'Technische Informatik I',
        'grade': '33', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF2001', 'subject': 'Mathematik II', 'grade': '19',
        'credits': '60', 'status': None, 'date': None},
    {'modul': 'T3INF2002', 'subject': 'Theoretische Informatik III',
        'grade': '15', 'credits': '60', 'status': None, 'date': None},
    {'modul': 'T3INF2003', 'subject': 'Software Engineering I',
        'grade': '10', 'credits': '90', 'status': None, 'date': None},
    {'modul': 'T3INF2004', 'subject': 'Datenbanken', 'grade': '12',
        'credits': '60', 'status': None, 'date': None},
    {'modul': 'T3INF2005', 'subject': 'Technische Informatik II',
        'grade': '23', 'credits': '80', 'status': None, 'date': None},
    {'modul': 'T3INF2006', 'subject': 'Kommunikations- und Netztechnik',
        'grade': '11', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF3001', 'subject': 'Software Engineering II',
        'grade': None, 'credits': None, 'status': None, 'date': None},
    {'modul': 'T3INF3002', 'subject': 'IT-Sicherheit', 'grade': '15',
        'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3_3101', 'subject': 'Studienarbeit', 'grade': None,
        'credits': None, 'status': None, 'date': None},
    {'modul': 'T3_1000', 'subject': 'Praxisprojekt I', 'grade': 'b',
        'credits': '200', 'status': None, 'date': None},
    {'modul': 'T3_2000', 'subject': 'Praxisprojekt II', 'grade': '15',
        'credits': '200', 'status': None, 'date': None},
    {'modul': 'T3_3000', 'subject': 'Praxisprojekt III',
        'grade': None, 'credits': None, 'status': None, 'date': None},
    {'modul': 'T3INF4104', 'subject': 'Elektrotechnik',
        'grade': '26', 'credits': '30', 'status': None, 'date': None},
    {'modul': 'T3INF4105', 'subject': 'Physik', 'grade': '14',
        'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF4302', 'subject': 'Systemarchitekturen der Informationstechnik',
        'grade': None, 'credits': None, 'status': None, 'date': None},
    {'modul': 'T3INF4303', 'subject': 'Computergraphik und Bildverarbeitung',
        'grade': None, 'credits': None, 'status': None, 'date': None},
    {'modul': 'T3INF4111',
        'subject': 'Grundlagen der Hard- und Software (MA-TINF19IT2)', 'grade': '16', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF4252', 'subject': 'Messdatenerfassung und -verarbeitung',
        'grade': '15', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3INF4275', 'subject': 'Business Process Management',
        'grade': '15', 'credits': '50', 'status': None, 'date': None},
    {'modul': 'T3_3300', 'subject': 'Bachelorarbeit', 'grade': None,
        'credits': None, 'status': None, 'date': None},
    {'modul': 'ZW_503.1',
        'subject': 'Ausbildung der Ausbilder - Modul 1 (T59_M1_G4)', 'grade': '30', 'credits': None, 'status': None, 'date': None},
    {'modul': 'ZW_503.2',
        'subject': 'Ausbildung der Ausbilder - Modul 2 (T60_M2_G6)', 'grade': '20', 'credits': None, 'status': None, 'date': None},
    {'modul': 'ZW_503.3',
        'subject': 'Ausbildung der Ausbilder - Modul 3 (T61_M3_G5)', 'grade': '12', 'credits': None, 'status': None, 'date': None},
]
