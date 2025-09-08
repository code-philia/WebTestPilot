from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

MODELS = {
    'gpt_mini': 'gpt-4o-mini',
    'o1': 'gpt-3.5-turbo',
    'gpt': 'gpt-4o',
    'gpt-4.1': 'gpt-4.1',
    'qwen_vl': 'qwen/qwen2.5-vl-32b-instruct:free',
}

def init_model(model='gpt'):
    model_name = MODELS.get(model, 'gpt-4o')
    return model_name

def create_model_chain(model='gpt'):
    model_name = MODELS.get(model, model)

    def invoke_model_chain(system_prompt, user_prompt, verbose=True, return_usage=False):
        client = None
        extra_args = {}

        if 'qwen' in model_name:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("Error: Environment variable OPENROUTER_API_KEY is not set.")
            
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            extra_args['extra_headers'] = {
                # "HTTP-Referer": "<YOUR_SITE_URL>", 
                # "X-Title": "<YOUR_SITE_NAME>",
            }
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Error: Environment variable OPENAI_API_KEY is not set.")
            
            client = OpenAI(api_key=api_key)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if isinstance(user_prompt, dict) and "content" in user_prompt:
            messages.append({"role": "user", "content": user_prompt["content"]})
        else:
            messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.0,
            max_tokens=512 if model_name in ['gpt-4o-mini', 'gpt-3.5-turbo'] else 256,
            **extra_args
        )
        
        result = response.choices[0].message.content
        if verbose:
            print("Response:")
            print(result)
            print("")
        
        # Return usage info if requested
        if return_usage and hasattr(response, 'usage'):
            return result, response.usage.total_tokens if response.usage else 0
        return result

    return invoke_model_chain


def create_single_user_message(user_prompt):
    return {
        "content": [
            {
                "type": "text",
                "text": user_prompt
            }
        ]
    }

def create_multimodal_user_message(text_inputs, base64_image):
    return {
        "content": [
            {
                "type": "text", "text": text_inputs
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                },
            }
        ]
    }