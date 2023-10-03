import os
import subprocess
from chroma import ChromaMemory
from .chain import Chain
from indices import FunctionIndex
from utils import get_gpt4_response, get_turbo_response
from utils import Logger
import datetime
import re
import logging
import json

import config

class Hyperion(Chain):

    _SYSTEM_MESSAGE = '''Current datetime: {datetime}. You will solve the user's task by choosing the right step to take. Your response must always be picked from the listed formats with swapped out curly brackets for values. You should beware of the context of the conversation and refer to the message history whenever necessary. \nRelevant memory from the past: {memory_text}'''

    # Transition pieces
    _COMMAND_TRANSITION = '''----\nPick one of the following responses:\n- THOUGHT: {your thoughts on what to do next, only if there's a clear plan or direction. Must be one sentence. Don't use this and use CONCLUSION if you have no further actions planned.}<END>\n- COMMAND: {command you will execute, make sure it is a valid Mac terminal executable command.}<END>\n- CONCLUSION: {a conclusion when you believe the current task is done. This piece of text could be final answer or follow up questions.}<END>\n----'''

    # Regexes
    _THOUGHT_REGEX = r"\s*THOUGHT:\s*(.*)"
    _COMMAND_REGEX = r"\s*COMMAND:\s*(.*)"
    _CONCLUSION_REGEX = r"\s*CONCLUSION:\s*(.*)"

    _index: FunctionIndex

    def __init__(self, index: FunctionIndex, logger: Logger):
        
        self._messages = []

        self._index = index
        self._logger = logger
        self.memory = ChromaMemory()


    def run(self, query: str, max_steps: int = 20):

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        sys_message = self._SYSTEM_MESSAGE.format(
            datetime=current_datetime,
            memory_text='No memory yet.'
        )
        self._messages = [{'role': 'system', 'content': sys_message}]

        self._add_user_message(query)
        self._add_user_message(self._COMMAND_TRANSITION)

        # conclusion_reached: bool = False
        generated_wrong_format: bool = False
        current_step: int = 0

        while (
            current_step < max_steps 
            # and not conclusion_reached
            and not generated_wrong_format
        ):
            if (verbose := os.environ.get('VERBOSE', False) == 'True'):
                print("----------\n Current message history is: ")
                for m in self._messages:
                    print(f"{m['role']}: {m['content']}")
                print("----------\n")
            
            response = get_gpt4_response(self._messages)['content']
            self.memory.store_memory(response)
            
            if 'THOUGHT' in response:
                self._handle_thought(response)
            elif 'COMMAND' in response:
                self._handle_command(response)
            elif 'CONCLUSION' in response or 'SUGGESTION' in response:
                self._handle_conclusion(response)
                # user inputs prompt again
                query = input('> ')
                self._add_user_message(query)
            else:
                # Hallucination
                self._logger.log(response, category='HALLUCINATION')
                generated_wrong_format = True
            current_step += 1

    def _handle_thought(self, response: str):
        thought = re.search(self._THOUGHT_REGEX, response).group(1)
        self._logger.log(thought, category='THOUGHT')
        self._add_assistant_message(f'THOUGHT: {thought}<END>')
        self._remove_transition_piece()

    def _handle_command(self, response: str):
        command = re.search(self._COMMAND_REGEX, response).group(1)
        self._logger.log(f'\n{command}', category='COMMAND')
        self._add_assistant_message(f'COMMAND: {command}<END>')
        self._remove_transition_piece()
        try:
            command_response = subprocess.check_output(command, shell=True).decode()
            command_response = command_response.replace('\n\n', '\n')
            self._logger.log(f'\n{command_response}\n', category='RESPONSE')
            self._add_user_message(f'RESPONSE: {command_response}')
            self._add_user_message(self._COMMAND_TRANSITION)
        except Exception as e:
            self._add_user_message(f'Error while executing command: {str(e)}')

    def _handle_conclusion(self, response: str):
        conclusion = re.search(self._CONCLUSION_REGEX, response).group(1)
        self._remove_transition_piece()
        self._logger.log(conclusion, category='CONCLUSION')
        self._add_assistant_message(f'CONCLUSION: {conclusion}<END>')

    def _add_user_message(self, message: str):
        self._messages.append({'role': 'user', 'content': message})

    def _add_assistant_message(self, message: str):
        self._messages.append({'role': 'assistant', 'content': message})

    def _remove_transition_piece(self):
        index = 0
        while index < len(self._messages):
            role = self._messages[index]['role']
            content = self._messages[index]['content']
            if (role == 'user' and
                content.startswith('----') and
                content.endswith('----')):
                self._messages.pop(index)
            index += 1
