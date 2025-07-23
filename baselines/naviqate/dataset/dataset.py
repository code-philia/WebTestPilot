import re

from datasets import load_dataset

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "text.usetex": False,
    "axes.labelsize": 15,
    "font.size": 12
})

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(project_dir)

from method.llm.llm_prompting import *
import method.llm.prompts as prompts
from method.utils.utils import load_json, save_json

def generate_action_sequence_description(model_chain, data):
    response = model_chain(
        prompts.action_sequence_description_prompt,
        create_single_user_message(data)
    )
    return response

def mind2web_to_json():
    

    dataset = load_dataset("osunlp/Mind2Web")

    output_data = [{'website': dp['website'], 'task': dp['confirmed_task'], 'actions': dp['action_reprs']} for dp in dataset['train']]

    output_file = 'tasks_mind2web.json'
    save_json(output_data, output_file)

def extract_parts(string, add_website_domain=False):
    match = re.search(r'(.*) in (\S+)$', string)
    if match:
        task = match.group(1).strip()
        website = match.group(2)
        if add_website_domain:
            if '.com' not in website:
                website += '.com'
        elif '.' in website:
            website = website[:website.find('.')]
        return task, website
    else:
        return None, None

def mind2web_live_abstracted_to_json():

    dataset = load_dataset("iMeanAI/Mind2Web-Live")

    filtered_dataset = [dp['task'] for dp in dataset['train']]

    model_chain_gpt = create_model_chain(init_model(model='gpt'))

    results = []

    for data in filtered_dataset:
        extracted_data = extract_parts(data)
        if extracted_data[0] is not None and extracted_data[1] is not None:
            response = model_chain_gpt(
                prompts.dataset_abstraction_prompt,
                create_single_user_message(extracted_data[0])
            )
            result = {
                "website": extracted_data[1],
                "task": response
            }
            results.append(result)

    output_file = 'abstracted_tasks.json'
    save_json(results, output_file)

    print(f"Results saved to {output_file}")

def mind2web_live_to_json(split='train'):
    dataset = load_dataset("iMeanAI/Mind2Web-Live")
    filtered_dataset = [dp['task'] for dp in dataset[split]]

    results = []

    for data in filtered_dataset:
        extracted_data = extract_parts(data)
        if extracted_data[0] is not None and extracted_data[1] is not None:
            result = {
                "website": extracted_data[1],
                "task": extracted_data[0]
            }
            results.append(result)

    output_file = 'tasks_mind2web_live_' + split + '.json'
    save_json(results, output_file)

    print(f"Results saved to {output_file}")

def find_mutual_tasks(json1, json2):

    json1_dict = {(item['website'], item['task']): item['actions'] for item in json1}
    tasks2 = {(item['website'], item['task']) for item in json2}
    mutual_tasks = [key for key in json1_dict.keys() if key in tasks2]
    mutual_list = [{"website": website, "task": task, "actions": json1_dict[(website, task)]} for website, task in mutual_tasks]
    return mutual_list

def cross_reference_datasets():

    json1 = load_json('tasks_mind2web.json')
    json2 = load_json('tasks_mind2web_live.json')

    mutual_objects = find_mutual_tasks(json1, json2)

    save_json(mutual_objects, 'reference_tasks.json')

    print("Mutual tasks saved to reference_tasks.json")


def generate_action_seq_dataset():

    model_chain = create_model_chain(init_model(model='gpt'))
    data = load_json("reference_tasks.json")

    output_data = [{'website': dp['website'], 'task': dp['task'], 'actions_desc': generate_action_sequence_description(model_chain, '\n'.join(dp['actions']))} for dp in data]
    output_file = 'reference_tasks_desc.json'
    save_json(output_data, output_file)


def add_categories():
    categories = {'exploretock': 'Travel',
    'enterprise': 'Travel',
    'kohls': 'Shopping',
    'united': 'Travel',
    'budget': 'Travel',
    'underarmour': 'Shopping',
    'kayak': 'Travel',
    'rottentomatoes': 'Entertainment',
    'parking': 'Travel',
    'amtrak': 'Travel',
    'amazon': 'Shopping',
    'us.megabus': 'Travel',
    'carmax': 'Shopping',
    'viator': 'Travel',
    'delta': 'Travel',
    'ultimate-guitar': 'Entertainment',
    'ticketcenter': 'Entertainment',
    'sixflags': 'Travel',
    'rei': 'Shopping',
    'newegg': 'Shopping',
    'imdb': 'Entertainment',
    'ign': 'Entertainment',
    'instacart': 'Shopping',
    'redbox': 'Entertainment',
    'booking': 'Travel',
    'uniqlo': 'Shopping',
    'airbnb': 'Travel',
    'tesla': 'Shopping',
    'soundcloud': 'Entertainment',
    'gamestop': 'Shopping',
    'tvguide': 'Entertainment',
    'seatgeek': 'Entertainment',
    'new.mta.info': 'Travel',
    'eventbrite': 'Entertainment',
    'nyc': 'Entertainment',
    'jetblue': 'Travel',
    'agoda': 'Travel',
    'espn': 'Entertainment',
    'mbta': 'Travel',
    'travelzoo': 'Travel',
    'amctheatres': 'Entertainment',
    'ryanair': 'Travel',
    'spothero': 'Travel',
    'expedia': 'Travel',
    'bookdepository': 'Shopping',
    'foxsports': 'Entertainment',
    'cvs': 'Shopping',
    'boardgamegeek': 'Entertainment',
    'target': 'Shopping',
    'aa': 'Travel',
    'cargurus': 'Shopping',
    'resy': 'Travel',
    'ebay': 'Shopping',
    'rentalcars': 'Travel',
    'kbb': 'Shopping',
    'last.fm': 'Entertainment',
    'sports.yahoo': 'Entertainment',
    'discogs': 'Entertainment',
    'qatarairways': 'Travel',
    'ikea': 'Shopping',
    'yelp': 'Travel',
    'cabelas': 'Shopping',
    'menards': 'Shopping',
    'store.steampowered': 'Entertainment',
    'carnival': 'Travel',
    'apple': 'Shopping',
    'marriott': 'Travel',
    'flightaware': 'Travel',
    'nps.gov': 'Travel',
    'yellowpages': 'Travel',
    'nfl': 'Entertainment',
    'thetrainline': 'Travel',
    'koa': 'Travel'}

    subd = {'exploretock': 'Travel.Restaurant',
    'enterprise': 'Travel.Car rental',
    'kohls': 'Shopping.Department',
    'united': 'Travel.Airlines',
    'budget': 'Travel.Car rental',
    'underarmour': 'Shopping.Fashion',
    'kayak': 'Travel.Airlines',
    'rottentomatoes': 'Entertainment.Movie',
    'parking': 'Travel.Other',
    'amtrak': 'Travel.Ground',
    'amazon': 'Shopping.General',
    'us.megabus': 'Travel.Ground',
    'carmax': 'Shopping.Auto',
    'viator': 'Travel.Other',
    'delta': 'Travel.Airlines',
    'ultimate-guitar': 'Entertainment.Music',
    'ticketcenter': 'Entertainment.Event',
    'sixflags': 'Travel.Other',
    'rei': 'Shopping.Speciality',
    'newegg': 'Shopping.Digital',
    'imdb': 'Entertainment.Movie',
    'ign': 'Entertainment.Game',
    'instacart': 'Shopping.General',
    'redbox': 'Entertainment.Movie',
    'booking': 'Travel.General',
    'uniqlo': 'Shopping.Fashion',
    'airbnb': 'Travel.Hotel',
    'tesla': 'Shopping.Auto',
    'soundcloud': 'Entertainment.Music',
    'gamestop': 'Shopping.Speciality',
    'tvguide': 'Entertainment.Movie',
    'seatgeek': 'Entertainment.Event',
    'new.mta.info': 'Travel.Ground',
    'eventbrite': 'Entertainment.Event',
    'nyc': 'Entertainment.Event',
    'jetblue': 'Travel.Airlines',
    'agoda': 'Travel.General',
    'espn': 'Entertainment.Sports',
    'mbta': 'Travel.Ground',
    'travelzoo': 'Travel.General',
    'amctheatres': 'Entertainment.Movie',
    'ryanair': 'Travel.Airlines',
    'spothero': 'Travel.Other',
    'expedia': 'Travel.General',
    'bookdepository': 'Shopping.Speciality',
    'foxsports': 'Entertainment.Sports',
    'cvs': 'Shopping.Speciality',
    'boardgamegeek': 'Entertainment.Game',
    'target': 'Shopping.General',
    'aa': 'Travel.Airlines',
    'cargurus': 'Shopping.Auto',
    'resy': 'Travel.Restaurant',
    'ebay': 'Shopping.General',
    'rentalcars': 'Travel.Car rental',
    'kbb': 'Shopping.Auto',
    'last.fm': 'Entertainment.Music',
    'sports.yahoo': 'Entertainment.Sports',
    'discogs': 'Entertainment.Music',
    'qatarairways': 'Travel.Airlines',
    'ikea': 'Shopping.Speciality',
    'yelp': 'Travel.Restaurant',
    'cabelas': 'Shopping.Speciality',
    'menards': 'Shopping.Speciality',
    'store.steampowered': 'Entertainment.Game',
    'carnival': 'Travel.Other',
    'apple': 'Shopping.Digital',
    'marriott': 'Travel.Hotel',
    'flightaware': 'Travel.Other',
    'nps.gov': 'Travel.Other',
    'yellowpages': 'Travel.Restaurant',
    'nfl': 'Entertainment.Sports',
    'thetrainline': 'Travel.Ground',
    'koa': 'Travel.Hotel'}

    file = 'abstracted_tasks_mind2web_live_test.json'
    dataset = load_json(file)

    for item in dataset:
        website = item.get('website')
        category = subd.get(website, 'Uncategorized')
        item['category'] = category

    save_json(dataset, file)

def plot_barchart_subdomain():
    file_path = '../evaluation/eval.csv'
    df = pd.read_csv(file_path)

    split_columns = df['subdomain'].str.split('.', n=1, expand=True)
    df['category'] = split_columns[0]
    df['subdomain_name'] = split_columns[1]

    df_grouped = df.groupby(['subdomain_name', 'category'])['naviqate'].apply(lambda x: (x == 'YES').mean()).reset_index()
    df_grouped.columns = ['subdomain_name', 'category', 'success_rate']
    df_grouped = df_grouped.sort_values(by='success_rate', ascending=False)

    categories = df['category'].unique()
    colors = plt.cm.get_cmap('Set1', len(categories))
    category_colors = {category: colors(i) for i, category in enumerate(categories)}

    plt.figure(figsize=(10, 4))
    bars = plt.bar(df_grouped['subdomain_name'], df_grouped['success_rate'] * 100, 
                color=[category_colors[cat] for cat in df_grouped['category']])

    plt.xlabel('Subdomain')
    plt.ylabel('Success Rate (%)')
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
<<<<<<< Updated upstream
    plt.gca().spines['top'].set_visible(True)
    plt.gca().spines['right'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)
    plt.gca().spines['bottom'].set_visible(True) 
=======
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(True)
>>>>>>> Stashed changes

    handles = [plt.Rectangle((0,0),1,1, color=category_colors[cat]) for cat in categories]
    plt.legend(handles, categories, title='Domain')

    plt.tight_layout()

    pdf_path = './subdomain_success_rate.pdf'
    plt.savefig(pdf_path, format='pdf')

    plt.show()


def plot_barchart_website():

    file_path = '../evaluation/eval.csv'
    df = pd.read_csv(file_path)
    
    df_grouped_website = df.groupby(['website', 'category'])['naviqate'].apply(lambda x: (x == 'YES').mean()).reset_index()
    df_grouped_website.columns = ['website', 'category', 'success_rate']
    df_grouped_website['website'] = df_grouped_website['website'].str.replace('.com', '', regex=False)
    df_grouped_website = df_grouped_website.sort_values(by='success_rate', ascending=False)

    categories = df['category'].unique()
    colors = plt.cm.get_cmap('Set1', len(categories))
    category_colors = {category: colors(i) for i, category in enumerate(categories)}

    plt.figure(figsize=(15, 4))
    bars = plt.bar(df_grouped_website['website'], df_grouped_website['success_rate'] * 100, 
                color=[category_colors[cat] for cat in df_grouped_website['category']])

    plt.xlabel('Website')
    plt.ylabel('Success Rate (%)')
    plt.ylim(0, 100)
<<<<<<< Updated upstream
    plt.xticks(rotation=70)
    plt.gca().spines['top'].set_visible(True)
    plt.gca().spines['right'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)
=======
    plt.xticks(rotation=45)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
>>>>>>> Stashed changes
    plt.gca().spines['bottom'].set_visible(True)

    handles = [plt.Rectangle((0,0),1,1, color=category_colors[cat]) for cat in categories]
    plt.legend(handles, categories, title='Domain')

    plt.tight_layout()

    pdf_path_website_updated = './website_success_rate.pdf'
    plt.savefig(pdf_path_website_updated, format='pdf')

# file = 'tasks_mind2web_live_test.json'
# dataset = load_json(file)
# column_str = "\n".join(map(str, [d['category'] for d in dataset]))
# # column_str.to_clipboard()
# print(column_str)

plot_barchart_website()
<<<<<<< Updated upstream
plot_barchart_subdomain()
=======
>>>>>>> Stashed changes


import json

def match_and_add_index(dataset_file, reference_file, output_file):
    # Load the dataset file (dataset.json)
    with open(dataset_file, 'r') as dataset_f:
        dataset = json.load(dataset_f)

    # Load the reference file (mind2web-test_104tasks_20240528.json)
    with open(reference_file, 'r') as reference_f:
        reference_data = json.load(reference_f)

    dataset_new = []

    # Iterate over each entry in dataset.json
    for i, dataset_entry in enumerate(dataset):
        # ref_entry = reference_data[i]
        dataset_idx = dataset_entry["index"]

        # # Look for a match in the reference file
        for ref_entry in reference_data:
            reference_idx = ref_entry["index"]

            # Check if the reference task is included in the dataset task
            if dataset_idx == reference_idx:
                dataset_entry['reference_task_length'] = ref_entry['reference_task_length']
                # If a match is found, add the "index" from reference file to dataset entry
        # dataset_entry["index"] = ref_entry["index"]
        # dataset_entry["evaluation"] = ref_entry["evaluation"]
        # dataset_entry["task"] = dataset_entry["task"] + " on " + dataset_entry["website"]
        # dataset_entry["reference_task_length"] = len(ref_entry["evaluation"])
        # del dataset_entry["website"]
                break  # Once matched, no need to search further for this entry
        dataset_new.append(dataset_entry)
    # Write the modified dataset to a new output file
    with open(output_file, 'w') as output_f:
        json.dump(dataset_new, output_f, indent=4)

    print(f"Modified dataset written to {output_file}")

# dataset_file = 'abstracted_tasks_mind2web_live_test.json'
<<<<<<< Updated upstream
# reference_file = 'tasks_mind2web_live_test.json'
# output_file = 'modified_dataset.json'

# # Run the matching function
# match_and_add_index(dataset_file, reference_file, output_file)
=======
# reference_file = 'mind2web-test_104tasks_20240528.json'
# output_file = 'modified_dataset.json'

# # Run the matching function
# match_and_add_index(dataset_file, reference_file, dataset_file)
>>>>>>> Stashed changes
