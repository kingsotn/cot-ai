from typing import List, Dict, Any
import openai
import os
import re


# GPT4_PROMPT_TOKEN_USEAGE = 0
# GPT4_COMPLE_TOKEN_USEAGE = 0

# TURBO_PROMPT_TOKEN_USEAGE = 0
# TURBO_COMPLE_TOKEN_USEAGE = 0


def get_gpt4_response(
        msg: Dict[str, str], 
        max_tokens: int=512, 
        stop: List[str]=['<END>']
    ) -> Dict[str, str]:
    
    # global GPT4_PROMPT_TOKEN_USEAGE
    # global GPT4_COMPLE_TOKEN_USEAGE
    response = openai.ChatCompletion.create(
        model='gpt-4',
        temperature=0,
        max_tokens=max_tokens,
        messages=msg,
        stop=stop,
    )

    # GPT4_PROMPT_TOKEN_USEAGE += response['usage']['prompt_tokens']
    # GPT4_COMPLE_TOKEN_USEAGE += response['usage']['completion_tokens']

    return dict(response['choices'][0]['message'])

def get_turbo_response(
        msg: Dict[str, str],
        max_tokens: int=64,
) -> Dict[str, str]:
    
    # global TURBO_PROMPT_TOKEN_USEAGE
    # global TURBO_COMPLE_TOKEN_USEAGE
    
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        messages=msg,
        max_tokens=max_tokens,
    )

    # TURBO_PROMPT_TOKEN_USEAGE += response['usage']['prompt_tokens']
    # TURBO_COMPLE_TOKEN_USEAGE += response['usage']['completion_tokens']

    return dict(response['choices'][0]['message'])

def get_completion_response(
        msg: str,
        max_tokens: int=64,
        model: str="text-davinci-003",
) -> Dict[str, str]:
    
    # extract 'id' fields from available openai models
    response = openai.Model.list()
    model_ids = [model['id'] for model in response['data']]

    if model not in model_ids:
        raise ValueError(f"Model {model} not found. Please choose from the following: {model_ids}")

    response = openai.Completion.create(
        engine=model,
        temperature=0,
        prompt=msg,
        max_tokens=max_tokens,
    )

    result = response['choices'][0]['text']

    return result

def get_embedding(text: str) -> List[float]:

    res = openai.Embedding.create(
        input=[text],
        engine="text-embedding-ada-002",
    )
    return res["data"][0]["embedding"]


# def show_usage():
#     cost = (GPT4_PROMPT_TOKEN_USEAGE / 1000) * 0.03 + (GPT4_COMPLE_TOKEN_USEAGE / 1000) * 0.06 
#     + ((TURBO_PROMPT_TOKEN_USEAGE + TURBO_COMPLE_TOKEN_USEAGE) / 1000) * 0.002
    
#     print('----------------------------------------')
#     print(f"GPT-4 PROMPT TOKENS: {GPT4_PROMPT_TOKEN_USEAGE} USED")
#     print(f"GPT-4 COMPLE TOKENS: {GPT4_COMPLE_TOKEN_USEAGE} USED")
#     print(f"TURBO PROMPT TOKENS: {TURBO_PROMPT_TOKEN_USEAGE} USED")
#     print(f"TURBO COMPLE TOKENS: {TURBO_COMPLE_TOKEN_USEAGE} USED")
#     print(f"TOTAL COST: ${cost:.5f}")
#     print('----------------------------------------')
