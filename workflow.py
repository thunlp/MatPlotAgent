import argparse
import json
import re

from tqdm import tqdm
from agents.query_expansion_agent import QueryExpansionAgent
from agents.plot_agent import PlotAgent
from agents.visual_refine_agent import VisualRefineAgent
import logging
import os
import shutil
import glob
import sys
from agents.utils import is_run_code_success, run_code, get_code
parser = argparse.ArgumentParser()
parser.add_argument('--workspace', type=str, default='./workspace')
parser.add_argument('--model_type', type=str, default='gpt-3.5-turbo')
parser.add_argument('--visual_refine', type=bool, default=True)
args = parser.parse_args()

def mainworkflow(expert_instruction, simple_instruction, workspace, max_try=3):
    # Query expanding
    logging.info('=========Query Expansion AGENT=========')
    config = {'workspace': workspace}
    query_expansion_agent = QueryExpansionAgent(expert_instruction, simple_instruction,model_type=args.model_type)
    expanded_simple_instruction = query_expansion_agent.run('simple')
    logging.info('=========Expanded Simple Instruction=========')
    logging.info(expanded_simple_instruction)
    logging.info('=========Plotting=========')

    # GPT-4 Plot Agent
    # Initial plotting
    action_agent = PlotAgent(config, expanded_simple_instruction)
    logging.info('=========Novice 4 Plotting=========')
    novice_log, novice_code = action_agent.run_initial(args.model_type, 'novice.png')
    logging.info(novice_log)
    logging.info('=========Original Code=========')
    logging.info(novice_code)
    # Code refinement
    # code_refine_agent = CodeRefineAgent(expanded_simple_instruction, novice_4_code)
    # refined_response = code_refine_agent.run()
    # logging.info('=========Refined Code=========')
    # logging.info(refined_response)

    # Visual refinement
    # if True:
    #     # refined_code = get_code(refined_response)
    #     # if refined_code == '':
    #     #    refined_code = refined_response.strip('"""')
    #     # else:
    #     #    pass
    #     refined_code = 'print(json.load())'
    #     if check_refined_code_executable(refined_code, 'gpt-4', 'novice', config['workspace']):
    #         print('Use refined code for visual feedback')
    #         visual_refine_agent = VisualRefineAgent('novice_4.png', config, refined_code, simple_instruction)
    #         visual_feedback = visual_refine_agent.run('gpt-4', 'novice', 'novice_4_final.png')
    #         logging.info('=========Visual Feedback=========')
    #         logging.info(visual_feedback)
    #         final_instruction = refined_code + '\n\n' + visual_feedback
    #         action_agent = PlotAgent(config, final_instruction)
    #         novice_4_log, novice_4_code = action_agent.run_vis('gpt-4', 'novice_4_final.png')
    #         logging.info(novice_4_log)
    #     else:
    if args.visual_refine and os.path.exists(f'{workspace}/novice.png'):
        print('Use original code for visual feedback')
        visual_refine_agent = VisualRefineAgent('novice.png', config, '', simple_instruction)
        visual_feedback = visual_refine_agent.run('gpt-4', 'novice', 'novice_final.png')
        logging.info('=========Visual Feedback=========')
        logging.info(visual_feedback)
        final_instruction = '' + '\n\n' + visual_feedback
        action_agent = PlotAgent(config, final_instruction)
        novice_log, novice_code = action_agent.run_vis(args.model_type, 'novice_final.png')
        logging.info(novice_log)

    # GPT-3.5-turbo Plot Agent
    # Initial plotting
    '''action_agent = PlotAgent(config, expanded_simple_instruction)
    logging.info('=========Novice 3.5 Plotting=========')
    novice_35_log, novice_35_code = action_agent.run_initial('gpt-3.5-turbo', 'novice_35.png')
    logging.info(novice_35_log)
    logging.info('=========Original Code=========')
    logging.info(novice_35_code)
    # Code refinement
    # code_refine_agent = CodeRefineAgent(expanded_simple_instruction, novice_35_code)
    # refined_response = code_refine_agent.run()
    # logging.info('=========Refined Code=========')
    # logging.info(refined_response)
    # Visual refinement
    if True:
        # refined_code = get_code(refined_response)
        # if refined_code == '':
        #     refined_code = refined_response.strip('"""')
        # else:
        #     pass
        refined_code = 'print(json.load())'
        if check_refined_code_executable(refined_code, 'gpt-3.5-turbo', 'novice', config['workspace']):
            print('Use refined code for visual feedback')
            visual_refine_agent = VisualRefineAgent('novice_35.png', config, refined_code, simple_instruction)
            visual_feedback = visual_refine_agent.run('gpt-3.5-turbo', 'novice', 'novice_35_final.png')
            logging.info('=========Visual Feedback=========')
            logging.info(visual_feedback)
            final_instruction = refined_code + '\n\n' + visual_feedback
            action_agent = PlotAgent(config, final_instruction)
            novice_35_log, novice_35_code = action_agent.run_vis('gpt-3.5-turbo', 'novice_35_final.png')
            logging.info(novice_35_log)
        else:
            print('Use original code for visual feedback')
            visual_refine_agent = VisualRefineAgent('novice_35.png', config, '', simple_instruction)
            visual_feedback = visual_refine_agent.run('gpt-3.5-turbo', 'novice', 'novice_35_final.png')
            logging.info('=========Visual Feedback=========')
            logging.info(visual_feedback)
            final_instruction = '' + '\n\n' + visual_feedback
            action_agent = PlotAgent(config, final_instruction)
            novice_35_log, novice_35_code = action_agent.run_vis('gpt-3.5-turbo', 'novice_35_final.png')
            logging.info(novice_35_log)'''


def check_refined_code_executable(refined_code, model_type, query_type, workspace):
    file_name = f'code_action_{model_type}_{query_type}_refined.py'
    with open(os.path.join(workspace, file_name), 'w') as f1:
        f1.write(refined_code)
    log = run_code(workspace, file_name)

    return is_run_code_success(log)


if __name__ == "__main__":

    workspace_base = args.workspace
    data_path = '/home/zhoupeng/project/LLM/agent/plotagent/benchmark/newPlotAgent/plot-agent/benchmark_data/'
    # open the json file 
    data = json.load(open(f'{data_path}/benchmark_instructions.json'))
    
    for item in tqdm(data):
        novice_instruction = item['simple_instruction']
        expert_instruction = item['expert_instruction']
        example_id = item['id']
        directory_path = f'{workspace_base}/example_{example_id}'

        # Check if the directory already exists
        if not os.path.exists(directory_path):
            # If it doesn't exist, create the directory
            os.mkdir(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
            input_path = f'{data_path}/data/{example_id}'
            if os.path.exists(input_path):
                #全部copy到f"Directory '{directory_path}'
                os.system(f'cp -r {input_path}/* {directory_path}')
        else:
            print(f"Directory '{directory_path}' already exists.")
            continue
        logging.basicConfig(level=logging.INFO, filename=f'{directory_path}/workflow.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        mainworkflow(expert_instruction, novice_instruction, workspace=directory_path)
