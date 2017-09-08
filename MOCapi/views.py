from django.shortcuts import render
from django.http import HttpResponse#
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return HttpResponse("Go away")

# Create your views here.
@csrf_exempt
def tracks(request):
    if request.method == 'GET':
        return HttpResponse("Go to getaway")
    else:
        if request.method == 'PUT':
            return HttpResponse("Putting on the Ritz")
        else:
            if request.method == 'POST':
                print(request.body)
                return HttpResponse("Return to sender")
            else:
                return 'Invalid method'
            
            
    