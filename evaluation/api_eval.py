import base64
import json
import logging
import os
import re
import shutil
import glob
import sys
sys.path.insert(0, sys.path[0]+"/../")
from agents.utils import is_run_code_success
from agents.plot_agent import PlotAgent
from openai import OpenAI
from agents.config.openai import API_KEY, BASE_URL, temperature


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def gpt_4_evaluate(code, query, image):
    if not os.path.exists(f'{image}'):
        executable = 'False'
    else:
        executable = 'True'

    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL, )

    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0.2,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f'''You are an excellent judge at evaluating generated code given an user query. You will be giving scores on how well a piece of code adheres to an user query by carefully reading each line of code and determine whether each line of code succeeds in carrying out the user query.
                        
                        A user query, a piece of code and an executability flag will be given to you. If the Executability is False, then the final score should be 0.


                         **User Query**: {query}

                         **Code**:
                         """
                         {code}
                         """
                         
                         **Executability**: {executable}
                         

 Carefully read through each line of code. Scoring can be carried out in the following aspect:
1. Code correctness (Code executability): Can the code correctly achieve the requirements in the user query? You should carefully read each line of the code, think of the effect each line of code would achieve, and determine whether each line of code contributes to the successful implementation of requirements in the user query. If the Executability is False, then the final score should be 0.

After scoring from the above aspect, please give a final score. The final score is preceded by the [FINAL SCORE] token.
For example [FINAL SCORE]: 40. A final score must be generated.''',
                    },
                ],
            }
        ],
        max_tokens=1000,
    )
    return response.choices[0].message


def gpt_4v_evaluate(ground_truth, image, rollback):
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,)
    if not os.path.exists(f'{image}'):
        if os.path.exists(f'{rollback}'):
            base64_image1 = encode_image(f"./benchmark_data/ground_truth/{ground_truth}")
            base64_image2 = encode_image(f"{rollback}")
        else:
            image = './benchmark_data/ground_truth/empty.png'
            base64_image1 = encode_image(f"{image}")
            base64_image2 = encode_image(f"{image}")
    else:
        base64_image1 = encode_image(f"./benchmark_data/ground_truth/{ground_truth}")
        base64_image2 = encode_image(f"{image}")

    response = client.chat.completions.create(
      model="gpt-4-vision-preview",
      temperature=0.2,
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": f'''You are an excellent judge at evaluating visualization plots between a model generated plot and the ground truth. You will be giving scores on how well it matches the ground truth plot.
               
               The generated plot will be given to you as the first figure. If the first figure is blank, that means the code failed to generate a figure.
               Another plot will be given to you as the second figure, which is the desired outcome of the user query, meaning it is the ground truth for you to reference.
               Please compare the two figures head to head and rate them.
               Suppose the second figure has a score of 100, rate the first figure on a scale from 0 to 100.
               Scoring should be carried out in the following aspect:
               1. Plot correctness: 
               Compare closely between the generated plot and the ground truth, the more resemblance the generated plot has compared to the ground truth, the higher the score. The score should be proportionate to the resemblance between the two plots.
               In some rare occurrence, see if the data points are generated randomly according to the query, if so, the generated plot may not perfectly match the ground truth, but it is correct nonetheless.
               Only rate the first figure, the second figure is only for reference.
               If the first figure is blank, that means the code failed to generate a figure. Give a score of 0 on the Plot correctness.
                After scoring from the above aspect, please give a final score. The final score is preceded by the [FINAL SCORE] token.
               For example [FINAL SCORE]: 40.''',
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image2}",
              },
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image1}",
              },
            },
          ],
        }
      ],
      max_tokens=1000,
    )
    return response.choices[0].message


def mainworkflow(test_sample_id, workspace, direct_eval=False):
    directory = f'{workspace}/example_{test_sample_id}'

    if not os.path.exists(directory):

        os.mkdir(directory)
        print(f"Directory '{directory}' created successfully.")
    else:
        print(f"Directory '{directory}' already exists.")

    logging.basicConfig(level=logging.INFO, filename=f'{directory}/eval_4v_rollback.log', filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    config = {'workspace': directory}

    with open('benchmark_data/benchmark_instructions.json') as file:
        data = json.load(file)
    simple_instruction = data[test_sample_id - 1]["simple_instruction"]
    expert_instruction = data[test_sample_id - 1]["expert_instruction"]

    if direct_eval:
        pass
    else:
        if test_sample_id in range(76, 101):
            # Define the source and destination directories
            source_dir = f'./benchmark_data/data/{test_sample_id}'
            destination_dir = directory
            # Create a list of all CSV files in the source directory
            csv_files = glob.glob(os.path.join(source_dir, '*.csv'))

            # Copy each CSV file to the destination directory
            for file in csv_files:
                # Extract the filename from the path
                filename = os.path.basename(file)
                # Copy the file
                shutil.copy(file, os.path.join(destination_dir, filename))

        logging.info('=========Plotting=========')

        action_agent = PlotAgent(config, expert_instruction, simple_instruction)
        logging.info('=========Novice 4 Plotting=========')
        logging.info(action_agent.run_novice('gpt-4', 'novice_4.png'))
        action_agent = PlotAgent(config, expert_instruction, simple_instruction)
        logging.info('=========Novice 3.5 Plotting=========')
        logging.info(action_agent.run_novice('gpt-3.5-turbo', 'novice_35.png'))

    for model_type in ['model_name']:
        for query_type in ['novice']:
            print(f'=========Evaluating {model_type} {query_type}=========')
            ground_truth = f"example_{test_sample_id}.png"
            logging.info(f'=========Evaluating {model_type} {query_type}=========')
            query = simple_instruction

            image = f'{directory}/novice_final.png'
            image_rollback = f'{directory}/novice.png'



            plot_result = gpt_4v_evaluate(ground_truth, image, image_rollback)
            logging.info(plot_result)




if __name__ == "__main__":
    # Get the number passed as an argument
    idx = int(sys.argv[1])
    directory_path = f'./your_workspace'
    mainworkflow(idx, workspace=directory_path, direct_eval=True)
