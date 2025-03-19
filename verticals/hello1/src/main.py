import json

import functions_framework

import requests

# TODO: Como habilitar invocacions sin autenticar ??

@functions_framework.http
def handler(request):
    data = request.get_json()

    # 1. add my own data
    data["frontto"]="SUCCESS"
    data["request"]={}


    # 2. make a GET request
    response = requests.get('https://httpbin.org/get')
    data["request"]["GET"] = response.json()

    # 3. make a POST request
    payload = {'name': 'Yaelita', 'age': 4}
    response = requests.post('https://httpbin.org/post', data=payload)
    data["request"]["POST"] = response.json()

    content = json.dumps(data)
    return content, 200