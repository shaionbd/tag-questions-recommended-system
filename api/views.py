import os
import pickle
import random

from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect
import requests
from sklearn import model_selection
import pandas as pd
import numpy as np
from sklearn.externals import joblib


# Create your views here.

def index(request):
    is_login = False
    if request.session.get('id'):
        return redirect('/recommend-questions')
    # context = {"is_login": is_login}
    return render(request, "pages/home.html")

#get features
def api(request):
    token = request.session['token']
    key = request.session['key']
    url = "https://api.stackexchange.com/2.2/me?key="+key+"&site=stackoverflow&order=desc&sort=reputation&access_token="+token+"&filter=!0Z-PEqoU*vLRLH1uOnw6JiCZP"
    response = requests.get(url)

    # get user info
    data = response.json()
    info = data['items']
    up_vote = info[0]['up_vote_count']
    down_vote = info[0]['down_vote_count']
    user_id = str(info[0]['user_id'])

    UpVotes = []
    DownVotes = []
    ajax = []
    android = []
    angularjs = []
    arrays = []
    aspnet = []
    bash = []
    csharp = []
    cpp = []
    database = []
    django = []
    html = []
    ios = []
    java = []
    javascript = []
    jquery = []
    mvc = []
    php = []
    python = []
    c = []
    css = []

    # UpVotes
    UpVotes.append(up_vote)

    # DownVotes
    DownVotes.append(down_vote)

    # ajax
    acceptCount, tags = call_api('ajax', user_id)
    ajax.append(int(acceptCount / len(tags) * 100))

    # android
    acceptCount, tags = call_api('android', user_id)
    android.append(int(acceptCount / len(tags) * 100))

    # angularjs
    acceptCount, tags = call_api('angularjs', user_id)
    angularjs.append(int(acceptCount / len(tags) * 100))

    # arrays
    acceptCount, tags = call_api('arrays', user_id)
    arrays.append(int(acceptCount / len(tags) * 100))

    # aspnet
    acceptCount, tags = call_api('asp.net', user_id)
    aspnet.append(int(acceptCount / len(tags) * 100))

    # bash
    acceptCount, tags = call_api('bash', user_id)
    bash.append(int(acceptCount / len(tags) * 100))

    # c#
    acceptCount, tags = call_api('c%23', user_id)
    csharp.append(int(acceptCount / len(tags) * 100))

    # c++
    acceptCount, tags = call_api('c++', user_id)
    cpp.append(int(acceptCount / len(tags) * 100))

    # database
    acceptCount, tags = call_api('database', user_id)
    database.append(int(acceptCount / len(tags) * 100))

    # django
    acceptCount, tags = call_api('django', user_id)
    django.append(int(acceptCount / len(tags) * 100))

    # html
    acceptCount, tags = call_api('html', user_id)
    html.append(int(acceptCount / len(tags) * 100))

    # ios
    acceptCount, tags = call_api('ios', user_id)
    ios.append(int(acceptCount / len(tags) * 100))

    # java
    acceptCount, tags = call_api('java', user_id)
    java.append(int(acceptCount / len(tags) * 100))

    # javascipt
    acceptCount, tags = call_api('javascript', user_id)
    javascript.append(int(acceptCount / len(tags) * 100))

    # jquery
    acceptCount, tags = call_api('jquery', user_id)
    jquery.append(int(acceptCount / len(tags) * 100))

    # mvc
    acceptCount, tags = call_api('mvc', user_id)
    mvc.append(int(acceptCount / len(tags) * 100))

    # php
    acceptCount, tags = call_api('php', user_id)
    php.append(int(acceptCount / len(tags) * 100))

    # python
    acceptCount, tags = call_api('python', user_id)
    python.append(int(acceptCount / len(tags) * 100))

    # c
    acceptCount, tags = call_api('c', user_id)
    c.append(int(acceptCount / len(tags) * 100))

    # css
    acceptCount, tags = call_api('css', user_id)
    css.append(int(acceptCount / len(tags) * 100))

    # for acceptance probability
    features = ['UpVotes', 'DownVotes']
    tags = ['javascript', 'java', 'c#', 'php', 'android', 'jquery', 'python', 'html', 'c++', 'ios', 'ajax',
            'angularjs', 'arrays', 'asp.net', 'mvc', 'bash', 'c', 'css', 'database', 'django']

    temp_answers_rate = {}
    temp_answers_rate = pd.DataFrame({
        'UpVotes': UpVotes,
        'DownVotes': DownVotes,
        'javascript': javascript,
        'java': java,
        'c#': csharp,
        'php': php,
        'android': android,
        'jquery': jquery,
        'python': python,
        'html': html,
        'c++': cpp,
        'ios': ios,
        'ajax': ajax,
        'angularjs': angularjs,
        'arrays': arrays,
        'asp.net': aspnet,
        'mvc': mvc,
        'bash': bash,
        'c': c,
        'css': css,
        'database': database,
        'django': django
    }, dtype=int)

    BASE = os.path.dirname(os.path.abspath(__file__))
    clf = joblib.load(BASE + '/templates/pkl/expert_model.pkl')
    #
    # current = {}
    # df = pd.DataFrame(current)
    #
    #
    temp_answers_rate.to_csv(BASE + "/templates/pkl/Probability.csv", index=False)
    #
    df = pd.read_csv(BASE + "/templates/pkl/Probability.csv", encoding='utf-8')
    df = df.fillna(method='ffill')  # fill the data that have null value
    subset_df = df[features + tags]
    x = subset_df.values
    expertise_tag = clf.predict(x)
    tag = expertise_tag[0]

    # Get all questions of tag
    # questions_url = "http://api.stackexchange.com/2.2/questions?pagesize=100&order=desc&sort=activity&tagged=" + tag + "&site=stackoverflow&filter=!5-dm_.B4H9vhG1gfS-0gSZokfV2rwNWoZq3g.J"
    # questions_response = requests.get(questions_url)
    # questions_data = questions_response.json()
    # questions = questions_data['items']

    return HttpResponse(tag)

def recommend_questions(request):

    user_id = request.session.get('id')
    #
    # 20 tag list for finding tags probability & recommondation system
    ### ---- {DownVotes, UpVotes, ajax, android, angularjs, arrays, asp.net, bash, c#, c++,
              # database, django, html, ios, java, javascript, jquery, mvc, php, python} --- ####

    UpVotes = []
    DownVotes = []
    ajax = []
    android = []
    angularjs = []
    arrays = []
    aspnet = []
    bash = []
    csharp = []
    cpp = []
    database = []
    django = []
    html = []
    ios = []
    java = []
    javascript = []
    jquery = []
    mvc = []
    php = []
    python = []
    c = []
    css = []

    # UpVotes
    UpVotes.append(23412)

    # DownVotes
    DownVotes.append(9123)

    # ajax
    acceptCount, tags = call_api('ajax', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    ajax.append(int(acceptCount / length  * 100))

    # android
    acceptCount, tags = call_api('android', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    android.append(int(acceptCount / length * 100))

    # angularjs
    acceptCount, tags = call_api('angularjs', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    angularjs.append(int(acceptCount / length * 100))

    # arrays
    acceptCount, tags = call_api('arrays', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    arrays.append(int(acceptCount / length * 100))

    # aspnet
    acceptCount, tags = call_api('asp.net', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    aspnet.append(int(acceptCount / length * 100))

    # bash
    acceptCount, tags = call_api('bash', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    bash.append(int(acceptCount / length * 100))

    # c#
    acceptCount, tags = call_api('c%23', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    csharp.append(int(acceptCount / length * 100))

    # c++
    acceptCount, tags = call_api('c++', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    cpp.append(int(acceptCount / length * 100))

    # database
    acceptCount, tags = call_api('database', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    database.append(int(acceptCount / length * 100))

    # django
    acceptCount, tags = call_api('django', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    django.append(int(acceptCount / length * 100))

    # html
    acceptCount, tags = call_api('html', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    html.append(int(acceptCount / length * 100))

    # ios
    acceptCount, tags = call_api('ios', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    ios.append(int(acceptCount / length * 100))

    # java
    acceptCount, tags = call_api('java', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    java.append(int(acceptCount / length * 100))

    # javascipt
    acceptCount, tags = call_api('javascript', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    javascript.append(int(acceptCount / length * 100))

    # jquery
    acceptCount, tags = call_api('jquery', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    jquery.append(int(acceptCount / length * 100))

    # mvc
    acceptCount, tags = call_api('mvc', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    mvc.append(int(acceptCount / length * 100))

    # php
    acceptCount, tags = call_api('php', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    php.append(int(acceptCount / length * 100))

    # python
    acceptCount, tags = call_api('python', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    python.append(int(acceptCount / length * 100))

    # c
    acceptCount, tags = call_api('c', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    c.append(int(acceptCount / length * 100))

    # css
    acceptCount, tags = call_api('css', user_id)
    if len(tags) == 0:
        length = 1
    else:
        length = len(tags)
    css.append(int(acceptCount / length * 100))

    # for acceptance probability
    features = ['UpVotes', 'DownVotes']
    tags = ['javascript', 'java', 'c#', 'php', 'android', 'jquery', 'python', 'html', 'c++', 'ios', 'ajax',
            'angularjs', 'arrays', 'asp.net', 'mvc', 'bash', 'c', 'css', 'database', 'django']
    #
    temp_answers_rate = {}
    temp_answers_rate = pd.DataFrame({
        'UpVotes': UpVotes,
        'DownVotes': DownVotes,
        'javascript': javascript,
        'java': java,
        'c#': csharp,
        'php': php,
        'android': android,
        'jquery': jquery,
        'python': python,
        'html': html,
        'c++': cpp,
        'ios': ios,
        'ajax': ajax,
        'angularjs': angularjs,
        'arrays': arrays,
        'asp.net': aspnet,
        'mvc': mvc,
        'bash': bash,
        'c': c,
        'css': css,
        'database': database,
        'django': django
    }, dtype=int)

    BASE = os.path.dirname(os.path.abspath(__file__))
    clf = joblib.load(BASE+'/templates/pkl/expert_model.pkl')
    #
    # current = {}
    # df = pd.DataFrame(current)
    #
    #
    # temp_answers_rate.to_csv(BASE+"/templates/pkl/Probability.csv", index=False)
    #
    # df = pd.read_csv(BASE+"/templates/pkl/Probability.csv",encoding ='utf-8')
    df = temp_answers_rate.fillna(method='ffill')  # fill the data that have null value
    subset_df = df[features + tags]
    x = subset_df.values
    expertise_tag = clf.predict(x)
    tag = expertise_tag[0]


    # Get all questions of tag
    questions_url = "http://api.stackexchange.com/2.2/questions?pagesize=100&order=desc&sort=activity&tagged="+tag+"&site=stackoverflow&filter=!5-dm_.B4H9vhG1gfS-0gSZokfV2rwNWoZq3g.J"
    questions_response = requests.get(questions_url)
    questions_data = questions_response.json()
    questions = questions_data['items']

    context = {"questions": questions,"expertise_tag": expertise_tag, "active_tag": tag}
    return render(request, "pages/questions.html", context)
    # return HttpResponse()
    # return HttpResponse(expertise_tag)
# destroy session data
def session_destroy(request):
    del request.session['id']
    del request.session['token']
    del request.session['key']
    return redirect("/")

# session create
def session_create(request):
    request.session['id'] = request.POST['userId']
    request.session['token'] = request.POST['token']
    request.session['key'] = request.POST['key']
    return HttpResponse("created")

def call_api(tag, user_id):
    tag_url = "https://api.stackexchange.com/2.2/users/" + user_id + "/tags/"+ tag +"/top-answers?pagesize=100&order=desc&sort=activity&site=stackoverflow&filter=!1zI20w-As3d74HiyS2l9r";
    tag_response = requests.get(tag_url)
    tag_data = tag_response.json()
    tags = tag_data['items']
    acceptCount = 0;
    for j in range(len(tags)):
        if tags[j]['is_accepted']:
            acceptCount = acceptCount + 1
    return acceptCount, tags
