import json
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm


def get_all_original_issues():
    all_issues = []
    apps = ["prestashop", "bookstack", "indico", "invoiceninja"]
    for app in apps:
        with open(f"./data/original/{app}.json", "r") as f:
            data = json.load(f)
        all_issues.extend(data)
    print("Total issues:", len(all_issues))
    return all_issues


all_issues = get_all_original_issues()

with open("./data/original/events.json", "r") as f:
    all_events = json.load(f)
crawled_ids = set([x["id"] for x in all_events])
print("Total events:", len(all_events), "crawled ids:", len(crawled_ids))

NUM_THREADS = 5
remaining_issues = [
    issue
    for issue in all_issues
    if "pull" not in issue["html_url"] and issue["html_url"] not in crawled_ids
]
# remaining_issues = remaining_issues[:11]
print("After filtering:", len(remaining_issues))


def crawl_event(issue: dict):
    try:
        issue_id = issue["html_url"]
        events_url = issue["events_url"]

        with requests.get(events_url) as r:
            if r.status_code != 200:
                print("Error fetching events for", issue_id)
                return {}

            events = r.json()

        return {"id": issue_id, "events": events}
    except Exception as e:
        print("Error in thread:", e)
        return {}


for start_idx in tqdm(range(0, len(remaining_issues), NUM_THREADS)):
    with ThreadPoolExecutor(max_workers=NUM_THREADS, thread_name_prefix="worker") as ex:
        results = ex.map(
            crawl_event,
            [
                remaining_issues[start_idx + i]
                for i in range(min(NUM_THREADS, len(remaining_issues) - start_idx))
            ],
        )

    for result in results:
        if result:
            all_events.append(result)
            with open("./data/original/events.json", "w") as f:
                json.dump(all_events, f, indent=4)

    time.sleep(1.5)
