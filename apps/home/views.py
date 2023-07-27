# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from .extract import extract_audio
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.conf import settings
from .forms import teamForm,vidForm,buyForm,meterForm,summForm,forumForm,ipfsForm
from .models import buy_energy,summary_file
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import base64
from .reading import read
from .topicpy import topic
from .keywords import key
from .summary import summarize
import os
from .file import combine
from .sentiment import get_sentiment_score
from .speech import transcript
# from .smart_meter_data_with_datetime import smart_meter
from.f_summary import f_summarize
import io
from .execution import *
from .keysentences import key_sentences
import base64
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import ipfsApi
from .detection import language
from .final_translate import final
from .duration import get_audio_duration
import ipfshttpclient

def retrieve_file_from_ipfs(request):
    d=ipfsForm(request.POST or None)
    ipfs_hash=request.POST.get('f_hash')
    try:
        # Connect to the IPFS HTTP API
        # api = ipfsApi.Client('127.0.0.1', 5001)
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

        # Retrieve the file from IPFS using its hash
        response = client.cat(ipfs_hash)

        # The response is a bytes object containing the file's content
        # You can save it to a file or process it as needed
        # For example, saving it to a local file:
        with open('file_from_ipfs.txt', 'wb') as f:
            f.write(response)

        print("File retrieved successfully from IPFS.")
    except ipfshttpclient.exceptions.ErrorResponse as e:
        print(f"Error retrieving file from IPFS: {e}")

    context={'file':response}

    html_template = loader.get_template('home/feedback.html')
    return HttpResponse(html_template.render(context, request))



def disussion(request):
    d=forumForm(request.POST or None)
    if d.is_valid():
        obj = d.save(commit=False)
        obj.save()
        name=obj.user_name
        ans=obj.answer

    context={'name':name,'ans':ans}

    html_template = loader.get_template('home/feedback.html')
    return HttpResponse(html_template.render(context, request))

def audio_upload(request):   
    form = summForm(request.POST or None, request.FILES or None)
    print(form.is_valid())
    if form.is_valid():
        temp=1
        obj = form.save(commit=False)
        obj.save()
        file_name=obj.p_name
        value=request.POST.get('slider_value')
        value=(int(value)*50)+200
        id=obj.id
        # file_path = settings.MEDIA_ROOT + '/new_files/'
        audio_path = settings.MEDIA_ROOT + '/new_audio/' + obj.uploadAudio.url.split('/')[-1]
        script=transcript(audio_path)
        summ_out=summarize(script,value)
        out=final(summ_out,audio_path)
        docname = f"output_{temp}.docx"
        fillle=combine(script,out,docname)
        file_path=settings.MEDIA_ROOT + '/new_transcripts/'

        api = ipfsApi.Client('127.0.0.1', 5001)
        res = api.add(file_path)[-1]['Hash']

       
    

        
    

        context = { 'p_name': file_name,'sum': out,'hash':res,'id':id}


        html_template = loader.get_template('home/summary.html')
        return HttpResponse(html_template.render(context, request))

    context = {'form' : form}
    html_template = loader.get_template('home/summary.html')
    return HttpResponse(html_template.render(context, request))

def video_upload(request):   
    form = vidForm(request.POST or None, request.FILES or None)
    print(form.is_valid())
    if form.is_valid():
        temp=1
        obj = form.save(commit=False)
        obj.save()
        file_name=obj.pv_name
        video_path = settings.MEDIA_ROOT + '/new_video/' + obj.uploadVideo.url.split('/')[-1]
        t=extract_audio(video_path)
        audio_path = "C://Users//sumit//Summarizer//media//new_audio//output.mp3"
        script=transcript(audio_path)
        summ_out=summarize(script)
        out=final(summ_out,audio_path)
        docname = f"output_{temp}.docx"
        fillle=combine(script,out,docname)
        file_path=settings.MEDIA_ROOT + '/new_transcripts/'

        api = ipfsApi.Client('127.0.0.1', 5001)
        res = api.add(file_path)[-1]['Hash']
    

        context = { 'pv_name': file_name,'sum': out,'hash':res}


        html_template = loader.get_template('home/video.html')
        return HttpResponse(html_template.render(context, request))

    context = {'form' : form}
    html_template = loader.get_template('home/video.html')
    return HttpResponse(html_template.render(context, request))




# def meter_analysis(request):
#     s=meterForm(request.POST or None)
#     if s.is_valid():
#         data=smart_meter()
#         print(data)

#     context={}

#     html_template = loader.get_template('home/analysis.html')
#     return HttpResponse(html_template.render(context, request))


def home(request):
    return render(request, 'home/home.html')


@login_required(login_url="/login/")
def get_time(request, id=None):
    summ = summary_file.objects.get(id=id)
    p=summ.p_name
    media=summ.uploadAudio
    number=get_audio_duration(media)/60
    duration = format(number, ".2f")
    path='C://Users//sumit//Summarizer//media//new_transcripts//new_trans.docx'
    t=read(path,1)
    print(t)
    words=key(t)
    topic_for_transcript=topic(t)
    sent=get_sentiment_score(t)
    print(topic_for_transcript)
    sentence=['Okay, and does this happen in any other settings? Uh, like sometimes when its really cold outside, Ill go out and like my chest feels tight and feel like I cant breathe and kind of sucks','Um, and, uh, in your family, has anybody ever had any of these similar symptoms before? Uh, like my, my dad, I think he maybe had also when he was younger, but like he doesnt really have it now','So, um, yeah, so they just told me to come back today','Okay, and how long does it take for the breathing difficulty to go away? Like if I stop doing like the thing Im doing it, I dont know, not very long, like a couple of minutes','Um, was there anything, was there anything that you tried besides the rest to make those symptoms go away? Like I have the uh, the inhaler that the doctor gave me last time']
    # sentences=key_sentences(t)
    link='#'
    if topic_for_transcript=="Heart Problem":
        link='heart.html'
    elif topic_for_transcript=="Kidney Problem":
        link='kidney.html'
    elif topic_for_transcript=="Skin Problem":
        link='skin.html'
    elif topic_for_transcript=="Diabetes":
        link='sugar.html'
    elif topic_for_transcript=="Urinary Problem":
        link='urinary.html' 
    elif topic_for_transcript=="Asthma":
        link='asthma.html'  
    elements = zip(words,words)
    
    context={'duration':duration,'p':p,'words':words,'topic':topic_for_transcript,'link':link,'sentiment':sent,'sentences':words ,'elements':elements}
    
    html_template = loader.get_template('home/analystics.html')
    return HttpResponse(html_template.render(context, request))




def buy_view(request):
    print("Hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    formb=buyForm(request.POST or None)
    print(formb.is_valid)
    if formb.is_valid():
        objb=formb.save(commit=False)
        objb.save()

        sellers = buy_energy.objects.all()
        context={
            'formb':formb, 
            'sellers':sellers,
                 }

        html_template = loader.get_template('home/buy_page.html')
        return HttpResponse(html_template.render(context,request))
    
    sellers = buy_energy.objects.all()
    for i in sellers:
        print(i.cus_name)
    context = { 'formb' : formb , 'sellers' : sellers } 

    html_template = loader.get_template('home/buy_page.html')
    return HttpResponse(html_template.render(context, request))




# def file_upload(request):   
#     form = hashForm(request.POST or None, request.FILES or None)
#     print(form.is_valid())
#     print("nisha")
#     if form.is_valid():
#         obj = form.save(commit=False)
#         obj.save()
#         print(obj.uploadfile.name)
#         file_path = settings.MEDIA_ROOT + '/new_cases/'
#         api = ipfsApi.Client('127.0.0.1', 5001)
#         res = api.add(file_path)[-1]['Hash']
#         file1=obj.uploadfile
#         name=obj.uploadfile_name
        
#         # a=UploadFile(uploadfile=file1,uploadfile_name=name)
#         # a.save()
#         # files = []
           

#         context = { 'hash': res}

#         html_template = loader.get_template('home/attendance.html')
#         return HttpResponse(html_template.render(context, request))

    # context = {'form' : form}
    # context={}
    # html_template = loader.get_template('home/attendance.html')
    # return HttpResponse(html_template.render(context, request))




def capCv(request):
    a=vidForm(request.POST or None)
    print("hi")
    if a.is_valid():
        obj = a.save(commit=False)
        obj.save()

        output=detect()
        # output=lipOut(v)
        # output='hi'
    context={}

    html_template = loader.get_template('home/capture.html')
    return HttpResponse(html_template.render(context, request))
@csrf_exempt
def capture_image(request):
    if request.method == 'POST':
        # Decode the base64 encoded image data
        image_data = request.POST.get('image')
        image_data = image_data.replace('data:image/png;base64,', '')
        image_data = base64.b64decode(image_data)
        # Create a PIL image object from the image data
        image = Image.open(io.BytesIO(image_data))
        # Create a directory if it does not exist
        if not os.path.exists('captures'):
            os.makedirs('captures')
        # Save the image to a file in the "captures" directory
        file_path = os.path.join('captures', 'captured_image.png')
        image.save(file_path)
        # Return a JSON response indicating success
        return JsonResponse({'status': 'success'})
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'status':'error'})


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def teamFun(request):
    a=teamForm(request.POST or None)
    if a.is_valid():
        obj=a.save(commit=False)
        obj.save()
        queryset=team.objects.all()
        context={'all_objects': queryset}

        html_template = loader.get_template('home/team.html')
        return HttpResponse(html_template.render(context, request))
    
    context={'all_objects':queryset}
    html_template = loader.get_template('home/team.html')
    return HttpResponse(html_template.render(context, request))    


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
