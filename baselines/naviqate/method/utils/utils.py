import torch
from scipy.spatial.distance import cosine
import json
import requests
import re
import base64
from PIL import Image
import io
from transformers import pipeline
import numpy as np
from sentence_transformers import SentenceTransformer, util
import math
import os
from io import BytesIO


class Actionable:
    def __init__(self, outerHTML, xpath, tagName, location, element):
        self.outerHTML = outerHTML
        self.xpath = xpath
        self.tagName = tagName
        self.location = location
        self.element = element

    
    def distance_from_point(self, point):
        x = self.location['x']
        y = self.location['y']
        pointx = point['x']
        pointy = point['y']
        return math.sqrt((x-pointx)**2 + (y-pointy)**2)


def encode_image(input_data, size=(1920, 1080)):
    if isinstance(input_data, (str, os.PathLike)):
        with open(input_data, "rb") as f:
            img = Image.open(f)
            img = img.convert("RGB")
    elif isinstance(input_data, bytes):
        with io.BytesIO(input_data) as temp_file:
            img = Image.open(temp_file)
            img = img.convert("RGB")
    elif isinstance(input_data, BytesIO):
        input_data.seek(0)
        img = Image.open(input_data)
        img = img.convert("RGB")
    else:
        raise TypeError("Unsupported input type for encoding")
    
    img = img.resize(size, Image.Resampling.LANCZOS)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    encoded_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return encoded_image

def get_similarity_score(task, elem, tokenizer, model):

    tokens_task = tokenizer(task, padding=True, truncation=True, return_tensors='pt')
    tokens_elem = tokenizer(elem, padding=True, truncation=True, return_tensors='pt')

    with torch.no_grad():
        embeddings1 = model(**tokens_task).last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings2 = model(**tokens_elem).last_hidden_state.mean(dim=1).squeeze().numpy()

    similarity_score = 1 - cosine(embeddings1, embeddings2)

    return similarity_score

def init_semantic_similarity_model():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

def get_semantic_similarity(model, source, sentences):

    sources = [
        source
    ]


    embeddings1 = model.encode(sources, convert_to_tensor=True)
    embeddings2 = model.encode(sentences, convert_to_tensor=True)

    cosine_scores = util.cos_sim(embeddings2, embeddings1)

    return cosine_scores.cpu().numpy().flatten()

def extract_integer_from_string(input_string):
    match = re.search(r'\d+', input_string)
    if match:
        return int(match.group())
    else:
        return None
    
def keep_top_n(list0, list1, scores, n=10):
    combined_list = list(zip(list0, list1, scores, range(len(list0))))
    sorted_list = sorted(combined_list, key=lambda x: x[2], reverse=True)
    result_list0 = [item0 for item0, item1, score, index in sorted_list[:n]]
    result_list1 = [item1 for item0, item1, score, index in sorted_list[:n]]
    result_scores = [score for item0, item1, score, index in sorted_list[:n]]
    return result_list0, result_list1, result_scores

def calculate_time_interval(start_time, end_time):

    interval_seconds = end_time - start_time

    hours = int(interval_seconds // 3600)
    minutes = int((interval_seconds % 3600) // 60)
    seconds = int(interval_seconds % 60)

    formatted_interval = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return formatted_interval

def to_json(items):
    formatted_items = {str(i): item.replace('"', r"'") for i, item in enumerate(items)}

    json_string = json.dumps(formatted_items, indent=4)

    return json_string

def json_to_list(json_string):
    start_index = json_string.find('{')
    end_index = json_string.rfind('}') + 1

    json_string = json_string[start_index:end_index]


    data_dict = json.loads(json_string)

    result_list = list(data_dict.values())

    return result_list

def init_captioner():
    captioner = pipeline("image-to-text",model="Salesforce/blip-image-captioning-base", max_new_tokens=100)
    return captioner

def run_inference_blip(captioner, image_src):

    response = requests.get(image_src)
    content_type = response.headers.get('content-type')
    
    if content_type not in ['image/jpeg', 'image/png', 'image/gif']:
        return None
    
    return captioner(image_src)[0]['generated_text']

def calculate_element_distance(last_action_coords, element_coords):
    x2, y2 = float(element_coords['x']), float(element_coords['y'])
    x1, y1 = float(last_action_coords['x']), float(last_action_coords['y'])
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def normalize_array(array):
    array = np.array(array, dtype=float)
    min_elem = np.min(array)
    max_elem = np.max(array)
    normalized_array = np.array((array - min_elem) / (max_elem - min_elem))
    return normalized_array

def sanitize_json(json_str):
    sanitized_json = ''.join(char for char in json_str if 31 < ord(char) < 127)
    return sanitized_json

def clean_json(s):
    s = sanitize_json(s)
    while True:
        try:
            json_regex = r'\{.*?\}'

            match = re.search(json_regex, s)

            if match:
                s = match.group()
                result = json.loads(s)

            break

        except Exception as e:

            if 'delimiter' in str(e):
                # position of unexpected character after '"'
                unexp = int(re.findall(r'\(char (\d+)\)', str(e))[0])
                # position of unescaped '"' before that
                unesc = s.rfind(r'"', 0, unexp)
                s = s[:unesc] + r'\"' + s[unesc+1:]
                # position of correspondig closing '"' (+2 for inserted '\')
                closg = s.find(r'"', unesc + 2)
                s = s[:closg] + r'\"' + s[closg+1:]

            elif 'quotes' in str(e):
                char = int(re.findall(r'\(char (\d+)\)', str(e))[0])
                s = s[:char] + '"' + s[char:]

            elif 'escape' in str(e):
                char = int(re.findall(r'\(char (\d+)\)', str(e))[0])
                s = s[:char] + '\\' + s[char:]
            else:
                print(e)
                print(s)
                exit(1)
    return s

def get_xpath(driver, object_id):
    return driver.execute_cdp_cmd("Runtime.callFunctionOn", {
                    "objectId": object_id,
                    "functionDeclaration": """
                        function() {
                            const xpathSegments = [];
                            let currentElement = this;
                            while (currentElement && currentElement.nodeType === Node.ELEMENT_NODE) {
                                let segment;
                                const parent = currentElement.parentNode;
                                if (parent) {
                                    const children = Array.from(parent.children);
                                    const sameTagSiblings = children.filter(child => child.tagName === currentElement.tagName);
                                    if (sameTagSiblings.length > 1) {
                                        const index = sameTagSiblings.indexOf(currentElement) + 1;
                                        segment = `${currentElement.tagName.toLowerCase()}[${index}]`;
                                    } else {
                                        segment = currentElement.tagName.toLowerCase();
                                    }
                                } else {
                                    segment = currentElement.tagName.toLowerCase();
                                }
                                xpathSegments.unshift(segment);
                                currentElement = parent;
                            }
                            return xpathSegments.length ? '/' + xpathSegments.join('/') : null;
                        }
                    """,
                    "returnByValue": True
                })['result']['value']

def modify_html(driver):
    js_script = """
    var clone = document.cloneNode(true);  // Clone the entire document
    clone.querySelectorAll('*').forEach(function(node) {
        var attrs = node.attributes;
        var keep = ['href', 'alt', 'aria-label', 'onclick', 'idx'];
        var remove = ['iframe', 'style', 'path', 'script', 'link'];
        for (var i = attrs.length - 1; i >= 0; i--) {
            var attrName = attrs[i].name;
            if (!keep.includes(attrName)) {
                node.removeAttribute(attrName);
            }
        }
        if (remove.includes(node.tagName.toLowerCase())) {
            node.parentNode.removeChild(node);
        }
    });
    var serializer = new XMLSerializer();
    return serializer.serializeToString(clone);
    """
    html_content = driver.execute_script(js_script)
    return html_content

def minify_html(driver):
    js_script = """
    var removeComments = function(node) {
        var child = node.firstChild;
        while (child) {
            if (child.nodeType === 8 || child.nodeType === 3 && !child.textContent.trim()) {
                var oldChild = child;
                child = child.nextSibling;
                node.removeChild(oldChild);
            } else {
                removeComments(child);
                child = child.nextSibling;
            }
        }
    };

    var removeEmptyElements = function(node) {
        var children = Array.from(node.childNodes);
        children.forEach(function(child) {
            if (child.nodeType === 1) { // Element node
                removeEmptyElements(child);
                if (!child.innerHTML.trim() && child.attributes.length === 0) {
                    child.parentNode.removeChild(child);
                }
            }
        });
    };

    removeComments(document);

    removeEmptyElements(document);

    var serializer = new XMLSerializer();
    var serialized = serializer.serializeToString(document);

    serialized = serialized.replace(/>\s+</g, '><').trim();

    document.open();
    document.write(serialized);
    document.close();
    """
    driver.execute_script(js_script)


def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def preprocess_element(outerHTML):
    res = outerHTML

    for attribute in ['style']:
        pattern = re.compile(rf'{attribute}="[^"]*"', re.IGNORECASE)
        res = pattern.sub('', outerHTML)

    path_pattern = r'<path[^>]*>.*?</path>'
    res = re.sub(path_pattern, '', res)

    svg_pattern = r'<svg[^>]*>.*?</svg>'
    res = re.sub(svg_pattern, '', res)


    if len(res) > 256:
        res = res[:256] + '>'
        
    return res


def extract_context(driver, actionables):
    context = []
    for a in actionables:
        xpath = a.xpath
        result = driver.execute_cdp_cmd('Runtime.evaluate', {
            'expression': f"""
            var target = document.evaluate('{xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            var allElements = document.querySelectorAll('*');
            var targetRect = target.getBoundingClientRect();
            var closeElements = [];

            function calcDistance(target, b) {{
                var distY = Math.abs(b.top - target.top);
                var distX = Math.abs(b.left - target.left);
                return Math.sqrt(distY * distY + distX * distX);
            }}

            allElements.forEach(el => {{
                if (el !== target) {{
                    var rect = el.getBoundingClientRect();
                    var distance = calcDistance(targetRect, rect);


                    if (distance < 50) {{ 
                        closeElements.push({{text: el.innerText, distance: distance}});
                    }}
                }}
            }});
            closeElements.sort((a, b) => a.distance - b.distance);
            closeElements = closeElements.slice(0, 5);
            closeElements.map(e => e.text.trim().slice(0, 50));
            """,
            'returnByValue': True
        })

        if 'result' in result and 'value' in result['result']:
            context.append(result['result']['value'])
        else:
            context.append([])

    return context




def create_context_json(actionables, close_elements):
    
    jsons = []

    for i, target_element in enumerate(actionables):
        d = {"outerHTML": target_element.outerHTML, "neighbours": [c for c in set(close_elements[i]) if len(c) > 1]}
        j = json.dumps(d)
        jsons.append(j)

    return jsons

def get_inner_text(driver, elem):
    innerText = None
    try:
        innerText = driver.execute_script("return arguments[0].innerText;", elem)
        if len(innerText) < 1:
            innerText = driver.execute_script("return arguments[0].aria-label;", elem)
        if len(innerText) < 1:
            innerText = driver.execute_script("return arguments[0].value;", elem)
        if len(innerText) < 1:
            innerText = driver.execute_script("return arguments[0].outerHTML;", elem)
    except:
        pass

    return innerText


def string_to_filename(s):

    s = s.replace(' ', '_')

    s = re.sub(r'[\/:*?"<>|]', '', s)

    s = re.sub(r'[^a-zA-Z0-9_\-]', '', s)
    return s


def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def init_rag():
    tasks_db = load_json('../dataset/RAG_reference_tasks.json')
    return tasks_db

def retreive_sample_tasks(model, tasks_db, task, n=3):
    sim = get_semantic_similarity(model, task, [t["original_task"] for t in tasks_db])

    idx = np.argsort(sim)[::-1]
    return [tasks_db[i] for i in idx[0:n]]