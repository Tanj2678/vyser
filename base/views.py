from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request

from .models import Room,Topic, Message
from .forms import RoomForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q


def loginRoom(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username= request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "user doesn't exist")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'invalid credentials')

    context = {'page':page}
    return render(request,'base/login_register.html', context)

def logoutRoom(request):
    logout(request)
    return redirect('home')

def registerRoom(request):
    form = UserCreationForm()
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'an error occured')
    context ={'form':form}
    return render(request, 'base/login_register.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'rooms': rooms,'topics':topics, 'room_messages':room_messages, 'user':user}
    return render(request, 'base/profile.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(host__username__icontains=q)|
        Q(description__icontains=q)|
        Q(name__icontains=q)
    )
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {'rooms': rooms,'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        if request.user.is_authenticated:
            mess = Message.objects.create(
                user = request.user,
                room = room,
                body = request.POST.get('body')
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)
        return redirect('login')
    context = {'room': room, 'room_messages':room_messages, 'participants':participants }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    # if request.method == 'POST':
    #     form = RoomForm(request.POST)
    #     if form.is_valid():
    #         room = form.save(commit=False)
    #         room.host = request.user
    #         room.save()
    #         return redirect('home')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            banner = request.FILES.get('banner'),
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context={'form':form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def editRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('you arent allowed here')
    # if request.method == 'POST':
    #     form = RoomForm(request.POST, instance=room)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('home')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.banner = request.FILES.get('banner')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context={'form':form, 'topics': topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('you arent allowed here')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context={'attr':room.name}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    room_messages = Message.objects.get(id=pk)
    if request.user != room_messages.user:
        return HttpResponse('you arent allowed here')
    if request.method == 'POST':
        room_messages.delete()
        return redirect('home')
    context={'attr':room_messages}
    return render(request, 'base/delete.html', context)



