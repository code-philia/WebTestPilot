import os
import json
from bs4 import BeautifulSoup
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(project_dir)

import method.utils.utils as utils
from lxml import etree

from lxml import etree

RED = "\033[91m"
GREEN = "\033[92m"
HIGHLIGHT = "\x1b[6;30;42m"
RESET = "\033[0m"
CYAN = '\033[96m'


def verify(folder_path, evaluations):
    
    try:
        html_files = sorted([file for file in os.listdir(folder_path) if file.endswith('.html')])


        json_file = folder_path + "/history.json"
        history = utils.load_json(json_file)
    except Exception:
        print("NOT EXISTS")
        return False

    if len(history) == 0:
        return False
    
    if len(html_files) > len(history):
        return False

    urls = [entry["url"] for entry in history if "url" in entry]

    verified = [False] * len(evaluations)

    dom_list = []

    for html_file in html_files:
        file_path = os.path.join(folder_path, html_file)
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml')
            dom = etree.HTML(str(soup))
            dom_list.append(dom)

    
    for i, evaluation in enumerate(evaluations):
        for j, dom in enumerate(dom_list):
            match_function_name = evaluation.get("match_function_name")
            # print(match_function_name)
            # print(j, match_function_name)
            
            if match_function_name == "url_exactly_match":
                url = evaluation.get("url")
                verified[i] = urls[j] == url
                # print(url, urls[j])

            elif match_function_name == "url_included_match":
                keys = evaluation.get("keys")
                # print(urls[j], keys)
                verified[i] = all([key.lower() in urls[j].lower() for key in keys])
                # print([key.lower() in urls[j].lower() for key in keys], keys, urls[j])

            elif match_function_name == "text_included_match":
                keys = evaluation.get("keys")
                text_content = "".join(dom.xpath("//text()")).strip()
                verified[i] = all([key.lower() in text_content.lower() for key in keys])
                # print(keys)

            elif match_function_name == "element_value_exactly_match":
                selector = evaluation.get("selector")
                value = evaluation.get("value")
                element = dom.cssselect(selector)
                if element:
                    element = element[0]
                else:
                    continue
                # print(element)
                verified[i] = element.get("value") == value

                if not verified[i] and element.tag == "select":
                    options = element.cssselect("option")
                    for option in options:
                        if option.get("value") == value and option.get("selected") == "selected":
                            verified[i] = True

                # print(value, element.get("value"))

            elif match_function_name == "element_value_conditional_match":
                selector = evaluation.get("selector")
                condition = evaluation.get("condition")
                element = dom.cssselect(selector)
                # print(selector)
                if element:
                    element = element[0]
                else:
                    continue
                val = element.get("value")
                if not val:
                    val = element.text.strip()
                if val:
                    verified[i] = eval(f"{val} {condition}")
                # print(condition, val)

            elif match_function_name == "element_text_exact_match":
                selector = evaluation.get("selector")
                text = evaluation.get("text")
                element = dom.cssselect(selector)
                if element:
                    element = element[0]
                else:
                    continue
                verified[i] = element.text.strip() == text
                
            elif match_function_name == "element_interaction_match":
                if j == len(dom_list) - 1:
                    continue
                selector = evaluation.get("selector")
                element = dom.cssselect(selector)
                if element:
                    element = element[0]
                else:
                    continue
                text = ''.join(element.itertext()).strip()
                text_content = "".join(dom_list[j+1].xpath("//text()")).strip()
                verified[i] = text.lower() in text_content.lower() 

            elif match_function_name == "element_boolean_match":
                selector = evaluation.get("selector")
                value = evaluation.get("value")
                element = dom.cssselect(selector)
                if element:
                    element = element[0]
                else:
                    continue
                verified[i] = element.get("checked") == value

            elif match_function_name == "element_attribute_match":
                selector = evaluation.get("selector")
                attribute = evaluation.get("attribute")
                value = evaluation.get("value")
                element = dom.cssselect(selector)
                if element:
                    element = element[0]
                else:
                    continue
                verified[i] = element.get(attribute) == value
                
            if verified[i]:
                break

    print(verified)
    return all(verified)


json_file_path = "../dataset/ground_truth_concrete.json"
webcanvas_SR = 0
num = 104


with open(json_file_path, 'r') as f:
    tasks = json.load(f)


for i in range(0, num):
    curr_task = tasks[i]
    output_dir = '../../WebCanvas/batch_tasks_results/example/out'
    task = curr_task.get("task")
    evaluations = curr_task.get("evaluation", [])
    idx = curr_task.get('index')
    folder_path = f'{output_dir}/{idx}'
    verification_result = verify(folder_path, evaluations)
    if verification_result:
        webcanvas_SR += 1
        print(f"{GREEN} Task {i} Passed {RESET}")
    else:
        print(f"{RED} Task {i} Failed {RESET}")

webcanvas_SR /= num
webcanvas_SR *= 100
print(f"{HIGHLIGHT} WEBCANVAS SR: {webcanvas_SR}% {RESET}")

SR = 0

for i in range(0, num):
    curr_task = tasks[i]
    output_dir = "./out/concrete"
    website = curr_task.get("website")
    if '.' not in website:
        website += '.com'
    task = curr_task.get("task")
    evaluations = curr_task.get("evaluation", [])
    folder_path = f'{output_dir}/{website}/{utils.string_to_filename(task)}'
    verification_result = verify(folder_path, evaluations)
    if verification_result:
        SR += 1
        print(f"{GREEN} Task {i} Passed {RESET}")
    else:
        print(f"{RED} Task {i} Failed {RESET}")
        
SR /= num
SR *= 100
print(f"{HIGHLIGHT} NAVIQATE SR: {SR}% {RESET}")

print(f"{CYAN} Improvement: {(SR-webcanvas_SR)*100/webcanvas_SR}% {RESET}")

