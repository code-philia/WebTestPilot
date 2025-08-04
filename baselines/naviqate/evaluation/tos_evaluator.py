import os
import json
import pandas as pd
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(project_dir)

from helper import get_additional_files
import method.utils.utils as utils

ds = utils.load_json('../dataset/tasks_mind2web_live_test.json')
csv_file = './abs_eval.csv'

eval_df = pd.read_csv(csv_file)

eval_yes_df = eval_df[eval_df['gpt4o'] == 'YES'][['mind2web_index']]
successful_tasks = list(eval_yes_df['mind2web_index'])

score = 0
num = 0

for task in ds:
    if task['index'] not in successful_tasks:
        continue
    website = task['website']
    task_name = task['task']
    if '.' not in website:
        website += '.com'
    
    actions, _ = get_additional_files(website, utils.string_to_filename(task_name), current_dir, abstracted=False, dir='../out/llm_only_round1')

    if actions is None:
        print(task_name, website)
        continue

    for action in actions:
        action_type = action["action"]
        action_type = action_type.split(":")[0]
        text = action_type.partition(":")[2] if ":" in action_type else ""
        if action_type == 'type' and len(text) == 0:
            actions.remove(action)
    
    score += task['reference_task_length']/len(actions)
    num += 1
    