from collections import defaultdict
from copy import deepcopy
import fnmatch
import json
import logging
import time
import re
from typing import Dict

def get_command(response_json: Dict):
    """
    Parses the response and returns the command name and arguments.

    This function will raise the exception `json.decoder.JSONDecodeError` if the response is not valid JSON.
    Any other error that occurs is also caught and the function returns an "Error:" message with the exception message.

    Args:
        response_json (Dict): The response from the AI in dictionary format.

    Returns:
        tuple: The command name and arguments, or some error indication.
               If the response json dictionary does not contain the 'command' key, or the value of
               'command' is not a dictionary, or the 'command' dictionary does not contain the 'name' key,
               returns a tuple where the first element is 'Error:' and the second element is a string explaining the problem.
               If some error occurs, returns a tuple where the first element is 'Error:' and the second element is the str of the exception.

    Raises:
        json.decoder.JSONDecodeError: If the response is not valid JSON.
        Exception: If any other error occurs.
    """
    try:
        if "command" not in response_json:
            return "Error:", "Missing 'command' object in JSON"

        if not isinstance(response_json, dict):
            return "Error:", f"'response_json' object is not dictionary {response_json}"

        command = response_json["command"]
        if not isinstance(command, dict):
            return "Error:", "'command' object is not a dictionary"

        if "name" not in command:
            return "Error:", "Missing 'name' field in 'command' object"

        command_name = command["name"]

        # Use an empty dictionary if 'args' field is not present in 'command' object
        arguments = command.get("args", {})

        return command_name, arguments
    except json.decoder.JSONDecodeError:
        return "Error:", "Invalid JSON"
    # All other errors, return "Error: + error message"
    except Exception as e:
        return "Error:", str(e)

import os
from contextlib import contextmanager

@contextmanager
def change_directory(directory):
    """
    A context manager that changes the current working directory to the specified directory, and then changes it back.
    # 示例用法
    with change_directory('./workspace'):
        # 在 ./workspace 目录中执行的代码
        print("Current Directory:", os.getcwd())

    # 在 with 块之外，已经切换回原来的目录
    print("Back to Original Directory:", os.getcwd())"""
    # 记录当前工作目录
    current_directory = os.getcwd()
    
    try:
        # 切换到指定目录
        print("Changing directory to:", directory)
        os.chdir(directory)
        yield  # 在这里执行 with 块中的代码
    finally:
        # 在退出 with 块后切换回原来的目录
        print("Changing directory back to:", current_directory)
        os.chdir(current_directory)

def get_workspace_structure(work_directory):
    """
    This function generates the structure of the workspace directory.
    
    Returns:
        dict: A dictionary depicting the structure of the workspace directory.
    """
    def generate_directory_structure(path):
        result = {'name':os.path.basename(path)}
        if os.path.isdir(path):
            result['type'] = 'directory'
            result['children'] = [generate_directory_structure(os.path.join(path,child)) for child in os.listdir(path)]
        else:
            result['type'] = 'file'
        return result
    return generate_directory_structure(work_directory)

def fill_in_placeholders(prompt_messages,placeholders: dict):
    """
    Fills in placeholders defined in the input with the corresponding values.
    
    Args:
        placeholders (dict): A dictionary containing keys as placeholders and values as their replacements.

    Returns:
        filled_messages: A copy of the initial prompt_messages with placeholders replaced with their corresponding values.
    """
    filled_messages = deepcopy(prompt_messages)
    
    for key, value in placeholders.items():
        if value is not None:
            filled_messages = filled_messages.replace("{{" + str(key) + "}}", str(value))
    return filled_messages

def _check_ignorement(path:str,ignored_list)->bool:
    for pattern in ignored_list:
        if fnmatch.fnmatch(path,pattern):
            return True
    return False

def print_filesys_struture(work_directory,return_root=False,max_entry_nums_for_level=100,ignored_list=[])->str:
    """Return a tree-like structure for all files and folders in the workspace. Use this tool if you are not sure what files are in the workspace.

    This function recursively walks through all the directories in the workspace
    and return them in a tree-like structure, 
    displaying all the files under each directory.
    
    Example:
    ```
    - root/
        - sub_directory1/
            - file1.txt
            - file2.txt
        - sub_directory2/
            - file3.txt
    ```

    :return string: The tree-like structure of the workspace.
    """
    full_repr = ''
    if return_root:
        full_repr += f'Global Root Work Directory: {work_directory}\n'

    folder_counts =  defaultdict(lambda: 0)
    for root, dirs, files in os.walk(work_directory):
        if _check_ignorement(root,ignored_list):
            continue
        level = root.replace(work_directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        folder_counts[root] += 1
        if folder_counts[root] > max_entry_nums_for_level:
            full_repr += f'{indent}`wrapped`\n'
        
        full_repr += f'{indent}- {os.path.basename(root)}/\n'
        
        idx = 0
        subindent = ' ' * 4 * (level + 1) + '- '
        for f in files:
            if _check_ignorement(f,ignored_list):
                continue
            
            idx += 1
            if idx > max_entry_nums_for_level:
                full_repr += f'{subindent}`wrapped`\n'
                break
            full_repr += f'{subindent}{f}\n'


    return full_repr


def get_code(response):
    # 匹配所有在```python和```之间的代码块
    all_python_code_blocks_pattern = re.compile(r'```python\s*([\s\S]+?)\s*```', re.MULTILINE)

    # 提取所有代码块并连接在一起
    all_code_blocks = all_python_code_blocks_pattern.findall(response)
    all_code_blocks_combined = '\n'.join(all_code_blocks)
    return all_code_blocks_combined


def run_code(workspace, code_file, log_file=None)->str:
    if log_file is None:
        log_file = code_file + '.log'
    with change_directory(workspace):
        #默认阻塞
        os.system(f'python "{code_file}" > "{log_file}" 2>&1')
        with open(log_file,'r') as f:
            log = f.read()
        # time.sleep(1)
    return log


def is_run_code_success(log):
    if 'Traceback (most recent call last):' in log or 'Error:' in log:
        return False
    else:
        return True

def get_error_message(log):
    if 'Traceback (most recent call last):' in log:
        return log.split('Traceback (most recent call last):')[1]
    elif 'Error:' in log:
        return log.split('Error:')[1]
    else:
        return 'Unknown Error'

def print_chat_message(messages):
    for message in messages:
        logging.info(f"{message['role']}: {message['content']}")
# if __name__ == "__main__":
#     print(print_filesys_struture('/home/zhoupeng/project/LLM/agent/plotagent/PlotAgent/workspace'))