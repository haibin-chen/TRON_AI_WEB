#from django.shortcuts import HttpResponse
from django.shortcuts import render

user_list = []

def index(request):
    #return HttpResponse("Hello world")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        my_dic = {'user': username, 'pwd': password}
        user_list.append(my_dic)
    return render(request, 'index.html', {'data':user_list})