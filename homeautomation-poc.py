# create a home automation bot with GPT4

import openai
import json
import datetime
import pytz
from dotenv import load_dotenv
import os

# load the contents of the .env file
load_dotenv()

# retrieve the value of the OPENAI_API_KEY variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# a couple of dummy functions for home automation

def turn_on(device):
    return_json={
        "device": device,
        "action": "on"
    }
    return json.dumps(return_json)

def turn_off(device):
    return_json={
        "device": device,
        "action": "off"
    }
    return json.dumps(return_json)


def get_temperature(sensor):
    return_json={
        "sensor": sensor,
        "temperature": 23
    }
    return json.dumps(return_json)


def set_temperature(sensor, temperature):
    return_json={
        "sensor": sensor,
        "temperature": temperature
    }
    return json.dumps(return_json)


def list_devices(kind):
    return_json={
        "devices": [
            "living room light",
            "kitchen light",
            "bedroom light",
        ],
        "sensors": [
            "living room",
            "bedroom",
            "outdoors"
        ]
    }
    return json.dumps(return_json)
    
def find_user_location(name):
    return "living room"

functions_list=[
    {
        "name": "turn_on",
        "description": "Turn on a device",
        "parameters": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "The device to turn on, e.g. living room light",
                }
            },
            "required": ["device"],
        },
    },
    {
        "name": "turn_off",
        "description": "Turn off a device",
        "parameters": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "The device to turn off, e.g. living room light",
                }
            },
            "required": ["device"],
        },
    },
    {
        "name": "get_temperature",
        "description": "Get the temperature from a sensor",
        "parameters": {
            "type": "object",
            "properties": {
                "sensor": {
                    "type": "string",
                    "description": "The sensor to get the temperature from, e.g. living room",
                }
            },
            "required": ["sensor"],
        },
    },
    {
        "name": "set_temperature",
        "description": "Set the temperature on a sensor",
        "parameters": {
            "type": "object",
            "properties": {
                "sensor": {
                    "type": "string",
                    "description": "The sensor to set the temperature on, e.g. living room",
                },
                "temperature": {
                    "type": "number",
                    "description": "The temperature to set, e.g. 23",
                }
            },
            "required": ["sensor", "temperature"],
        },
    },
    {
        "name": "list_devices",
        "description": "List all devices and sensors",
        "parameters": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "description": "The kind of devices to list, e.g. lights or sensors",
                }
            },
            "required": ["kind"],
        },
    },
    {
        "name": "find_user_location",
        "description": "Find the room the user is in",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The user's name, if known, e.g. John",
                }
            },
            "required": ["name"],
        },
    },
]

available_functions = {
    "turn_on": turn_on,
    "turn_off": turn_off,
    "get_temperature": get_temperature,
    "set_temperature": set_temperature,
    "list_devices": list_devices,
    "find_user_location": find_user_location
}

messages = []
messages.append({"role": "system", "content": '''You are a home automation bot. You can turn on and off devices, and read the temperature on sensors.
You can set the temperature on sensors too if they support it. You can search for the room the user is in.
You can also list all devices and sensors and you use that to find out what you can do.
You are here to help the user automate their home.
'''})

def get_chatgpt_response(prompt):
    
    while True:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions_list,
            function_call="auto",
        )
        response_message = response["choices"][0]["message"]

        # Check if the model wants to call a function
        if response_message.get("function_call"):
            # call the function
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            print("   GPT wants to call function: " + function_name + " with arguments: " + str(function_args))
            function_response = function_to_call(**function_args)
            print("   Function response: " + str(function_response))

            # add the function response to the messages
            messages.append(response_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                })
            print("    Repeat function call loop")
        else:
            # the model does not want to call a function
            print("    No further function calls needed.")
            if response_message["role"] == "assistant":
                return response_message["content"]            
            break

    return response_message["content"]

# main loop
while True:
    prompt = input("You: ")
    messages.append({"role": "user", "content": prompt})
    response = get_chatgpt_response(prompt)
    print("Bot: " + response)
    messages.append({"role": "assistant", "content": response})


