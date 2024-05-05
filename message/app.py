import json
import boto3
import yaml
# import requests

MODEL_NAME = "gpt-3.5-turbo"
PROMPT_FILE = "./config/prompts.yaml"
MAX_TOKENS = 500

with open(PROMPT_FILE, 'r') as file:
    prompts_dict = yaml.safe_load(file)


def process_message(json_data, sources=None):
    # Connect to LLM lambda
    client = boto3.client('lambda')

    invoke_params = {
        "FunctionName": "CC-LLM-Service-Stack-HitLLMFunction-MSEMwT1OvOzE",
        "InvocationType": "RequestResponse",
        "Payload": json.dumps(json_data)
    }

    response = client.invoke(**invoke_params)
   
    payload = json.loads(response['Payload'].read().strip().decode('utf-8'))
    formed_response = {
        'statusCode': payload['statusCode'],
        'text': payload['body']
    }

    if sources:
        formed_response['sources'] = sources
    else:
        formed_response['sources'] = []

    return formed_response


def message(event, context):
    print("in message lambda")

    token = event.get('token', '')

    if token == "G=0H2>:y3QJl.>$Nu{N;7i`m7vKzP~wzj;$Wv<5oCv)Le30fJ0%WlC,<D2rXr~7":
    
        post_body = {
            "messages": event.get('messages', []),
        }

        print("post_body: ", post_body)
        
        last_message = post_body['messages'][-1].get('text', '')

        print("last_message: ", last_message)

        # Make sure to hit guardrails lambda
        # checks = await check_guardrails(last_message)
        checks = {
            'greetings': False,
            'restricted': False,
            'questions': True,
        }
        
        if checks['greetings'] == True:
            print("in greetings")
            return process_message(json_data={
                    "model" : MODEL_NAME,
                    "prompt" : prompts_dict["greeting_template"].replace('{INPUT}', last_message),
                    "stream" : False,
                    "max_tokens" : MAX_TOKENS,
                })
            
        if checks['restricted'] == True:
            
            return {
            'statusCode': 200,
            'body': {"text": "Sorry we cannot answer that question. That is restricted.", "sources": []}
            }
            # return JSONResponse(content={"text": "Sorry we cannot answer that question. That is restricted.", "sources": []}) 
        
        if checks['questions'] == True:
            # Update to hit context lambda
            # context = await fetch_context(last_message)
            return process_message(json_data={
                "model" : MODEL_NAME,
                "prompt" : prompts_dict["question_answer_template_2"].replace('{INPUT}', last_message).replace('{CONTEXT}', context['context']),
                "stream" : False,
                "max_tokens" : MAX_TOKENS,
            })
            # }, sources=context['sources'])
                
        return {
            'statusCode': 200,
            'body': {"text": "Sorry we cannot answer that question. We will work on this.", "sources": []}
            }
        # return JSONResponse(content={"text": "Sorry we cannot answer that question. We will work on this.", "sources": []})
    else:
        return {
            'statusCode': 200,
            'body': {"text": "Invalid token", "sources": []}
        }
        # return JSONResponse(content={"text": "Invalid token", "sources": []})

