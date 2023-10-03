import sys
import io

from typing import List
from functions import Function

class Interpreter(Function):
    @property
    def name(self) -> str:
        return 'python_interpreter'
    
    @property
    def description(self) -> str:
        return 'Write Python code and run it through this function. You must use print() statement for there to be any output.'
    
    def execute(self, code: str) -> str:
        code = code.replace('```', '')
        code = code.replace('```python', '')
        code = code.replace('"', '')
        
        # Create a new output stream
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        # Try to execute the code
        try:
            exec(code)
        except Exception as e:
            print("An error occurred: ", e)
        finally:
                    # Reset the standard output
            sys.stdout = old_stdout

        # Get the output and return it
        response = redirected_output.getvalue()
        if response.endswith('\n'):
            response = response[:-1]
        return response
