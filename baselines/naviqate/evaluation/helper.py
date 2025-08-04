import sys
import os
import json
import pandas as pd
import xlsxwriter

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(project_dir)

import method.utils.utils as utils

def get_additional_files(website, task, base_dir, abstracted=False, dir=None):
    task_dir = os.path.join(base_dir, 'out/round2', website, task)
    if abstracted:
        task_dir = os.path.join(base_dir, 'out-abstracted', website, task)
    if not os.path.exists(task_dir):
        task_dir = os.path.join(base_dir, 'out-original', website, task)
    if dir:
        task_dir = os.path.join(base_dir, dir, website, task)
    if not os.path.exists(task_dir):
        return None, None
    json_file = os.path.join(task_dir, 'history.json')
    if not os.path.exists(json_file):
        return None, None
    json_file = utils.load_json(json_file)
    
    
    screenshots = []
    for file in sorted(os.listdir(task_dir)):
        if file.endswith('.png'):
            screenshots.append(os.path.join(task_dir, file))
    
    screenshots = screenshots[:20]
    
    return json_file, screenshots

def create_excel():
    # user_tasks_file = os.path.join(project_dir, 'dataset', 'tasks_mind2web_live_test.json')
    abstracted_tasks_file = os.path.join(project_dir, 'dataset', 'abstracted_tasks_mind2web_live_test.json')
    
    # with open(user_tasks_file) as f:
    #     user_tasks_data = json.load(f)
        
    with open(abstracted_tasks_file) as f:
        abstracted_tasks_data = json.load(f)

    # user_tasks_processed = []
    # for i, task in enumerate(user_tasks_data):
    #     website = task['website']
    #     if '.' not in website:
    #         website += '.com'
    #     task_name = task['task']
    #     json_file, screenshots = get_additional_files(website, utils.string_to_filename(task_name), current_dir)
    #     row = {
    #         'index': i,
    #         'task': task_name,
    #         'website': website,
    #         'steps': json_file,
    #         # 'screenshots': screenshots
    #     }
    #     user_tasks_processed.append(row)

    abstracted_tasks_processed = []
    for i, task in enumerate(abstracted_tasks_data):
        website = task['website']
        if '.' not in website:
            website += '.com'
        task_name = task['task']
        json_file, screenshots = get_additional_files(website, utils.string_to_filename(task_name), current_dir, abstracted=True)
        row = {
            'index': i,
            'task': task_name,
            'website': website,
            'steps': json_file,
            # 'screenshots': screenshots
        }
        abstracted_tasks_processed.append(row)

    # user_tasks_df = pd.DataFrame(user_tasks_processed)
    abstracted_tasks_df = pd.DataFrame(abstracted_tasks_processed)

    # Create an Excel file using xlsxwriter
    workbook = xlsxwriter.Workbook('tasks_data.xlsx')
    
    # user_tasks_sheet = workbook.add_worksheet('User_Tasks')
    abstracted_tasks_sheet = workbook.add_worksheet('Abstracted_Tasks')

    def write_headers(sheet, df):
        col_num = 0
        for col in df.columns:
            if col == 'steps':
                for i in range(20): 
                    sheet.write(0, col_num + i, f'step{i+1}')
                col_num += 20
            else:
                sheet.write(0, col_num, col)
                col_num += 1

    # write_headers(user_tasks_sheet, user_tasks_df)
    write_headers(abstracted_tasks_sheet, abstracted_tasks_df)

    
    def write_data_and_images(sheet, df):
        for row_num, row_data in enumerate(df.itertuples(), 1):
            for col_num, value in enumerate(row_data[1:]):
                if col_num == 3:
                    steps = value
                    if steps:
                        for i, step in enumerate(steps):
                            if i >= 20:
                                break
                            sheet.write(row_num, col_num + i, 'element: ' + step['element'] + '\naction: ' + step['action'])
                    col_num += 20
                else:
                    sheet.write(row_num, col_num, value)
                    col_num += 1

    # write_data_and_images(user_tasks_sheet, user_tasks_df)
    write_data_and_images(abstracted_tasks_sheet, abstracted_tasks_df)

    workbook.close()
    print("Excel file created successfully with sheets 'User_Tasks' and 'Abstracted_Tasks'.")


if __name__ == "__main__":
    create_excel()



