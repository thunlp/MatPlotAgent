import logging
import re
import openai
from regex import E
import tenacity
from agents.config.openai import API_KEY, BASE_URL, temperature
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential, stop_after_delay,
)
from models.model_config import MODEL_CONFIG


def print_chat_message(messages):
    for message in messages:
        logging.info(f"{message['role']}: {message['content']}")

@retry(wait=wait_random_exponential(min=0.02, max=1), stop=(stop_after_delay(10) | stop_after_attempt(100)))
def completion_with_backoff(messages, model_type):
    # if  model_type.find('codellama_instruct') != -1:
    #     return codellama_generate(messages, model_type)
    # elif model_type.find('deepseek') != -1:
    #     return deepseek_generate(messages, model_type)
    if model_type in MODEL_CONFIG.keys():
        # openai.api_base = "http://localhost:8000/v1"
        # openai.api_key = API_KEY
        port = MODEL_CONFIG[model_type]['port']
        model_full_path= MODEL_CONFIG[model_type]['model']
        
        openai_api_key = "EMPTY"
        openai_api_base = f"http://localhost:{port}/v1"

        client = openai.OpenAI(
            # defaults to os.environ.get("OPENAI_API_KEY")
            api_key=openai_api_key,
            base_url=openai_api_base,
        )
        try:
            response = client.chat.completions.create(
                # model="gpt-3.5-turbo-1106",
                model=model_full_path,
                messages=messages,
                temperature=temperature,
                timeout=30*60,#30分钟
                max_tokens=4096,
                
            )
            result = response.choices[0].message
            answer = result.content
            return answer
        except KeyError:
            # print("Error in message chat completions.")
            # print(json.dumps(response))
            return None
        except openai.BadRequestError as e:
            # print("Error in message chat completions.")
            # print(json.dumps(response))
            return e
        
            # print(json.dumps(response))
            

    else:
        openai.api_key = API_KEY
        openai.base_url = BASE_URL
        # client = openai.Client(api_key=API_KEY, base_url=BASE_URL)
        try:
            response = openai.chat.completions.create(
            # model="gpt-3.5-turbo-1106",
            model=model_type,
            messages=messages,
            temperature=temperature,
        )
        # API返回回答
            result = response.choices[0].message
            answer = result.content
            return answer
        except KeyError:
            # print("Error in message chat completions.")
            # print(json.dumps(response))
            return None
        except openai.BadRequestError as e:
            # print("Error in message chat completions.")
            # print(json.dumps(response))
            return e


def completion_with_log(messages, model_type, enable_log=False):
    if enable_log:
        logging.info('========CHAT HISTORY========')
        print_chat_message(messages)
    response = completion_with_backoff(messages, model_type)
    if enable_log:
        logging.info('========RESPONSE========')
        logging.info(response)
        logging.info('========RESPONSE END========')
    return response


def completion_for_4v(messages, model_type):
    openai.api_key = API_KEY
    openai.base_url = BASE_URL
    # client = openai.Client(api_key=API_KEY, base_url=BASE_URL)
    response = openai.chat.completions.create(
        # model="gpt-3.5-turbo-1106",
        model=model_type,
        messages=messages,
        temperature=temperature,
        max_tokens=1000
    )
    # API返回回答
    result = response.choices[0].message
    answer = result.content
    return answer


def construct_message_for_chatgpt(prompt_list):
    msg = []
    roles = ["user", "assistant"]

    for i, prompt in enumerate(prompt_list):
        msg.append({
            "role": roles[i%2], "content": prompt
        })
        
    assert msg[-1]["role"] == "user"
    return msg