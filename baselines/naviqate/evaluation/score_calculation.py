import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from urllib.parse import urlparse
from helper import get_additional_files
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(project_dir)

import method.utils.utils as utils

class ModalHandler:
    def __init__(self, driver):
        self.driver = driver

    def close_modals_and_backdrops(self):
        keywords = ["modal", "backdrop", "modal-backdrop"]
        for keyword in keywords:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(@class, '{keyword}') or contains(@id, '{keyword}') or contains(local-name(), '{keyword}')]")
                for element in elements:
                    try:
                        self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element)
                    except WebDriverException as e:
                        print(f"Error removing element containing '{keyword}': {e}")
                time.sleep(1)
            except Exception as e:
                print(e)


class StepEvaluator:
    def __init__(self, driver):
        self.driver = driver

    def evaluate_step(self, current_url, xpath, value, expected_url, expected_xpath, expected_value):
        print(current_url)
        url_score = self.url_exact_match(current_url, expected_url)
        path_score = self.path_exact_match(xpath, expected_xpath)
        value_score = self.value_exact_match(value, expected_value)

        total_score = url_score + path_score + value_score
        return total_score

    def url_exact_match(self, input_url, reference_url):
        return 1 if input_url == reference_url else 0

    def path_exact_match(self, input_xpath, reference_xpath):
        return 1 if input_xpath == reference_xpath else 0

    def value_exact_match(self, input_value, reference_value):
        return 1 if input_value == reference_value else 0

def find_element_by_preprocessed_html(driver, target_html):
    # Get all elements in the page
    all_elements = driver.find_elements(By.XPATH, "//*")

    for element in all_elements:
        try:
            # Get the outerHTML of the element using JavaScript execution
            outer_html = driver.execute_script("return arguments[0].outerHTML;", element)

            # Preprocess the element's outerHTML
            processed_html = utils.preprocess_element(outer_html)


            # Compare the processed HTML with the target
            if target_html in processed_html:
                print("Element found!")
                return element

        except Exception as e:
            print(f"Error processing element: {e}")
    
    print("Element not found!")
    return None

class ActionExecutor:
    def __init__(self, driver):
        self.driver = driver

    def do_action(self, action):
        xpath = action["xpath"]
        action_type = action["action"]
        outer_html = action["element"][:-1]
        print(outer_html)
        action = action_type.split(":")[0]
        text = action_type.partition(":")[2] if ":" in action_type else ""

        try:
            element = self.driver.find_element(By.XPATH, xpath)
        except Exception as e:
            try:
                element = find_element_by_preprocessed_html(self.driver, outer_html)
            except Exception as e:
                print('ERRRRRR')
                return
        try:
            if action == 'select':
                if element.tag_name == 'select':
                    select = Select(element)
                    select.select_by_index(int(text) - 1)
                else:
                    action = 'click'

            if action == 'click':
                ActionChains(self.driver).move_to_element(element).click(element).perform()

            if action == 'type':
                print("text:", text)
                if len(text) > 2:
                    element.clear()
                    element.send_keys(Keys.SPACE, Keys.BACK_SPACE)
                ActionChains(self.driver).move_to_element(element).click(element).perform()
                if "checkbox" not in outer_html:
                    element.send_keys(text)
                    element.send_keys(Keys.RETURN)

        except Exception as e:
            print(e)
            try:
                if action == 'type':
                    element.send_keys(text)
                    # element.submit()
                    element.send_keys(Keys.RETURN)
                else:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    element.click()
            except Exception as e:
                print(e)
                print(xpath)
                return 1


def calculate_score(website, actions, ref_task):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"window-size=1920,1080")

    driver = uc.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get("https://"+website)

    # modal_handler = ModalHandler(driver)
    # modal_handler.close_modals_and_backdrops()


    action_executor = ActionExecutor(driver)
    evaluator = StepEvaluator(driver)

    # reference_task_length = ref_task["reference_task_length"]
    last_step_eval = ref_task['evaluation'][-1]  # Get the evaluation for the last step

    expected_url = last_step_eval["content"]["url"]
    expected_xpath = last_step_eval["content"].get("reference_answer", "")
    expected_value = last_step_eval["content"].get("reference_answer", "")

    # Execute all actions before evaluating the last step
    for action in actions:
        action_executor.do_action(action)


        current_url = driver.current_url
        xpath = action["xpath"]
        action_type = action["action"]
        text = action_type.split(":")[1] if ":" in action_type else ""
        

        step_score = evaluator.evaluate_step(current_url, xpath, text, expected_url, expected_xpath, expected_value)
        if step_score == 1:
            break
    

        time.sleep(2)

    print(f"score for task '{ref_task['task']}': {step_score}")

    # # Now evaluate the last action
    # if len(actions) >= 1:
    #     last_action = actions[-1]  # Get the last action based on task length

    #     current_url = driver.current_url
    #     xpath = last_action["xpath"]
    #     action_type = last_action["action"]
    #     text = action_type.split(":")[1] if ":" in action_type else ""

    #     # Evaluate the last step
    #     step_score = evaluator.evaluate_step(current_url, xpath, text, expected_url, expected_xpath, expected_value)
    #     print(f"score for task '{ref_task['task']}': {step_score}")
    

    driver.quit()

def remove_empty_type_actions(data):
    # Load the JSON file

    # Filter the actions where "type" has text after ":"
    filtered_data = []
    for item in data:
        action_type = item.get("action", "")
        
        # Check if the action is a "type" action and it contains text after ":"
        if action_type.startswith("type:"):
            # Extract the text part after "type:"
            text = action_type.partition(":")[2]
            
            # Only keep the item if there is non-empty text
            if text.strip():
                filtered_data.append(item)
        elif action_type == "type":
            # This case catches the "type" without a colon
            continue
        else:
            # Keep actions that are not "type"
            filtered_data.append(item)


    return filtered_data


def main():
    user_tasks_file = os.path.join(project_dir, 'dataset', 'tasks_mind2web_live_test.json')

    with open(user_tasks_file, "r") as f:
        user_tasks_data = json.load(f)

    
    for i, task in enumerate(user_tasks_data):
        website = task['website']
        if '.' not in website:
            website += '.com'
        task_name = task['task']
        index = task['index']
        actions, _ = get_additional_files(website, utils.string_to_filename(task_name), current_dir)
        actions = remove_empty_type_actions(actions)


        calculate_score(website, actions, task)
        
     



if __name__ == "__main__":
    main()
