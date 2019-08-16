from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from tron.tron_logic import *

user_list = []

def index(request):
    '''
    return HttpResponse("Hello world")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        my_dic = {'user': username, 'pwd': password}
        user_list.append(my_dic)
    return render(request, 'index.html', {'data':user_list})
    '''
    return render(request, 'index.html')

@csrf_exempt
def ajax_test(request):
    all_position = request.POST.get("position")
    my_position = request.POST.get("my_position")
    # ai control red!
    opponent_position = request.POST.get("opponent_position")

    board, player_x, player_y = build_board(all_position, my_position, opponent_position)
    game = TronGame(board)
    ai_tron_game = PlayerAgent(1)
    a = ai_tron_game.choose_move(game)
    #print("recommend:", a)
    if a[0] - player_x == 1 and a[1] - player_y == 0:
        return_json = {"x": 1, "y": 0}
    elif a[0] - player_x == 0 and a[1] - player_y == 1:
        return_json = {"x": 0, "y": 1}
    elif a[0] - player_x == -1 and a[1] - player_y == 0:
        return_json = {"x": -1, "y": 0}
    elif a[0] - player_x == 0 and a[1] - player_y == -1:
        return_json = {"x": 0, "y": -1}
    else:
        return_json = {"x": 0, "y": 1}

    #return_json = {"x": 0, "y": 1}
    return HttpResponse(json.dumps(return_json), content_type='application/json')
