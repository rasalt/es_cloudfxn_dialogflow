def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'

def getDialogflowParams(req):
    sess = req["sessionInfo"]

    if 'parameters' in sess:
        param = sess["parameters"]
    else:
        param = None
    return param

def getDialogflowIntent(req):
    param = req["fulfillmentInfo"]
    intent = param["tag"]
    return intent

def getDialogflowText(req):
    return req['text']


                
from flask import request, make_response
import json  
session={}


def populate(req, intent, params):
    text = ""
    print(params)
    print("---------------")
    ## Personalization - birthdate
    from datetime import datetime, date
    
    # Populate the params
    # Plan info
 
    return text, params

def get_token():
    if 1:
        from google.auth import default
        from google.auth.transport.requests import Request, AuthorizedSession

        credentials, project_id = default()
        
        if credentials.token is None:
            print("RK: Token is None")
            adapter = Request()
            credentials.refresh(adapter)
            if credentials.token is None:
                print("RK: Token is STILL None")

        session = AuthorizedSession(credentials)
        resp = session.request('GET', 'https://www.googleapis.com/storage/v1/b')
        print(resp.status_code)
        return credentials.token
    else:
        from google.auth import default
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        credentials, project_id = default()
        if credentials is None:
            raise ValueError("Could not get default credentials")
        elif credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise ValueError("Credentials are not valid")
        print("---- token ----")
        print(credentials.token)    
        return credentials.token
    
        return "34334"

def es_askquestion(convId, question):
    import json
    import requests

    headers = {'Authorization': 'Bearer {}'.format(get_token()),
        'Content-Type': 'application/json'
    }
    query = {}
    query['input'] = question
    
    print("query-----------")
    print(query)
    
    data = {}
    data['query'] = query

    data = json.dumps(data)

    print(data)
    print(headers)
    print("----------Query------------")
    requesturl = 'https://discoveryengine.googleapis.com/v1beta/projects/<PROJECT_NUM>/locations/global/collections/default_collection/dataStores/<ES_STORE_NUM>/conversations/{}:converse'.format(convId)
    print("------ requesturl ------")
    print(requesturl) 
    print("Request is ---------\n")
    print(headers)
    print(data) 
    #params = {'api_key': 'AIzaSyCmRC1PcJNcsr3rYD5syob-SCIvaWeBdEk'}

    response = requests.post(requesturl, headers=headers, data=data)
    #resposne = requests.post(requesturl, data = data, params = params)
#    print(response.json())
    print(response.text)
    response_str = json.loads(response.text)
    print(json.dumps(response_str))
    print("*****************-------*****************")
    if ('reply' in response_str) and ('reply' in response_str['reply']):
        finalresponse = response_str['reply']['reply']
        if 'searchResults' in response_str:
            for s in response_str['searchResults']:
                source = s['document']['derivedStructData']['link']
                finalresponse = finalresponse + "\n" + source
                print(" Source is {}".format(source))
                        
    print(finalresponse)
    return finalresponse
    return finalresponse, params

def es_createconnection():
    import requests


    headers = {'Authorization': 'Bearer {}'.format(get_token()),
        'Content-Type': 'application/json'
    }
    data = '''{
        'user_pseudo_id': 'thisconvo'
    }'''

    #print(headers)
    print("-------Conversation setup---------------")
    url = 'https://discoveryengine.googleapis.com/v1beta/projects/<PROJECT_NUM>/locations/global/collections/default_collection/dataStores/<ES_STORE_NUM>/conversations'
    #params = {'api_key': 'AIzaSyCmRC1PcJNcsr3rYD5syob-SCIvaWeBdEk'}
    #response = requests.post(url, data = data, params=params)
    
    response = requests.post(url, headers=headers, data=data)

    #response = requests.post(url, data = data, params=params)
    print("---------create connection response-----------")
    print(response.json())
    print("---------create connection response-----------")
    print(type(response))
    response = response.json()
    resp_name = response['name']
    resp_name_array = resp_name.split('/')
    convId = resp_name_array[-1]
    return convId

def webhook(request):
     
    req = request.get_json() 
    print(" REQUEST IS: {}".format(req))  
    params = getDialogflowParams(req)
    intent = getDialogflowIntent(req)

        
   
    print("**********************")
    print("INTENT is {}".format(intent))

    if intent == "knowledge":
        # Check if the params has a connection id 
        if 'es_convId' in params:
            convId = params['es_convId']
        else:
            #Create a connection 
            params['es_convId'] = es_createconnection()
            convId = params['es_convId']
        val = es_askquestion(convId, getDialogflowText(req))


    print("Val is {}".format(val))  
    webhookresponse = {}
    webhookresponse['fulfillment_response'] = {}
    webhookresponse['fulfillment_response']['messages'] = []


    
    webhookresponse['sessionInfo'] = {}
    webhookresponse['sessionInfo']['parameters'] = params

    message = {}
    message['text'] = {}
    message['text']['text'] = []
    message['text']['text'].append(val)

    webhookresponse['fulfillment_response']['messages'].append(message)
   
    print("Webhookresponse is {}".format(webhookresponse))
    resp = json.dumps(webhookresponse, indent=4)
    r = make_response(resp)
    r.headers['Content-Type'] = 'application/json'
    return r


