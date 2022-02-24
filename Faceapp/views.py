from django.shortcuts import render
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from tensorflow.keras.applications import VGG16
from django.core.files.storage import FileSystemStorage
import tensorflow as tf
import os
from .models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from django.shortcuts import redirect
from tensorflow.python.keras.backend import reverse

from django.contrib.auth.models import User
from django.contrib import auth
import random

img_height, img_width = 206, 278

model_graph = tf.compat.v1.Graph()
with model_graph.as_default():
   tf_session = tf.compat.v1.Session()
   with tf_session.as_default():
       model = load_model('./models/except_hurt_aug.h5')

# Create your views here.
def index(request):
    context={'a':1}
    return render(request, 'Faceapp/index.html', context)

def predictImage(request):
    if str(request.user) == 'AnonymousUser':
        return redirect('/login')
    else:
        print(request)
    #    print(request.Post['emotion'])
        fileObj=request.FILES['filePath']
        fs=FileSystemStorage()
        filePathName = fs.save(fileObj.name, fileObj)
        filePathName = fs.url(filePathName)
        testimage='.'+filePathName
        img = image.load_img(testimage, target_size=(img_height,img_width))
        img_tensor = image.img_to_array(img)
        img_tensor = np.expand_dims(img_tensor, axis=0)#axis=0 or 1은 행열 붙이는 방향을 의미
        img_tensor /= 255.# RGB 계수와 연관이 있는 값
        with model_graph.as_default():
            with tf_session.as_default():
                predi=model.predict(img_tensor)
                result = np.argmax(predi)+1
                emotion_dt = datetime.now().strftime("%m%d")
        # emotion = Emotion(content=result, emotion_dt=emotion_dt, content_str=result_text)
        # emotion.save()
        user = request.user


        emotion_list = ['Anger', 'Embarassment', 'Happy', 'Neutrality', 'Sad', 'Unrest']
        result_text = emotion_list[result-1]
        comment = request.POST['comment']
        emotion = Emotion(content=result, emotion_dt=emotion_dt, content_str=result_text, comment=comment, author=user)
        emotion.save()

        # 1. 분노, 2. 당황, 3. 행복, 4. 중립, 5. 슬픔, 6. 불안 (3,4번 사이 상처였으나 삭제) 
        music_video = Music.objects.filter(emotion_code=result)
        shuffle_video = random.choice(music_video)

        context={'filePathName':filePathName, 'predict':result_text, 'music_video':shuffle_video}
        return render(request,'Faceapp/index.html',context) 

def mood_calendar(request):
    if str(request.user) == 'AnonymousUser':
        return redirect('/login')
    else:
        user = request.user
        emotion = Emotion.objects.filter(author_id=user)
        # emotion = Emotion.objects.all()
        context={ 'emotion':emotion }

        #date = Emotion.objects.get(created_at)
        #result = Emotion.objects.get(content)
        #context={'date':date, 'result':result}
        return render(request, 'Faceapp/mood_calendar.html', context)

def note(request):
    if str(request.user) == 'AnonymousUser':
        return redirect('/login')
    else:
        return render(request, 'Faceapp/note.html')


# def viewDataBase(request):
#     listOfImages=os.listdir('./media/')
#     listOfImagesPath=['./media/'+i for i in listOfImages]
#     context={'listOfImagesPath':listOfImagesPath}
#     return render(request,'viewDB.html',context) 

def mypage(request):
    if str(request.user) == 'AnonymousUser':
        return redirect('/login')
    else:
        user = request.user
        emotion_results = Emotion.objects.filter(author_id=user)
        # emotion_results = Emotion.objects.all()

        array = []
        for Emotion.object in emotion_results:
            array.append(Emotion.object.content_str)
        unique_emotion = list(set(array))
        
        dd = {}
        for emotion1 in unique_emotion:
            dd[emotion1] = array.count(emotion1)

        context = {
            'graph_labels': list(dd.keys()),
            'graph_values': list(dd.values()),
            'emotions': emotion_results
        }
        return render(request, 'Faceapp/mypage.html', context)


def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:
            user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1']
            )
            auth.login(request, user)
            return redirect('/')
        return render(request, 'signup.html')

    return render(request, 'Faceapp/signup.html')


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'Faceapp/login.html', {'error':'username or password is incorrect!'})
    else:
        return render(request, 'Faceapp/login.html')


def logout(request):
    auth.logout(request)
    return redirect('/')
