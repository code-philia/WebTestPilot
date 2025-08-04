import sys
import os
import json
import time
from selenium.common.exceptions import WebDriverException

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

sys.path.append(project_dir)

import method.utils.utils as utils
from method.crawler.crawler import WebCrawler
import method.utils.logger as logging

def eval():
    logger = logging.get_logger()
    with open('../dataset/tasks_mind2web_live_test.json') as f:
        d = json.load(f)
        logger.info(f"NUMBER OF SAMPLES: {len(d)}")
        for i in range(len(d)): 
            task = d[i]['task']
            website = d[i]['website']

            if '.' not in website:
                website += '.com'
                            
            logger.info('•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••')
            logger.info(f"TASK {i}: {task}")
            logger.info(f"WEBSITE: {website}, MAX_STEPS: 20")
            start_time = time.time()

            try:

                crawler = WebCrawler(website, task, abstracted=False, headless=False, output_dir='./out/concrete')
                crawler.loop(MAX_STEPS=20)

            except WebDriverException as e:
                logger.error(f"An error occurred: {e} - Skipping Task {i}")
                continue

            end_time = time.time()
            logger.info(f"DURATION: {utils.calculate_time_interval(start_time, end_time)}")

if __name__ == "__main__":
    eval()
