# 导入所需的库
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 新增了 qwen_vl 模型
MODELS = {
    'gpt_mini': 'gpt-4o-mini',
    'o1': 'gpt-3.5-turbo',
    'gpt': 'gpt-4o',
    'gpt-4.1': 'gpt-4.1',
    'qwen_vl': 'qwen/qwen2.5-vl-32b-instruct:free',
}

# init_model 函数
def init_model(model='gpt'):
    model_name = MODELS.get(model, 'gpt-4o')
    return model_name

def create_model_chain(model='gpt'):
    # 兼容传入简称（如 'gpt'）或完整模型名
    # 如果 model 是字典中的简称，则获取其对应的完整名称；否则直接使用 model
    model_name = MODELS.get(model, model)

    def invoke_model_chain(system_prompt, user_prompt, verbose=True, return_usage=False):
        # 客户端不再是全局的，而是在这里根据模型名称动态创建
        client = None
        extra_args = {} # 用于存放非 OpenAI 官方接口可能需要的额外参数

        # 判断是否为 Qwen 模型，并配置对应的客户端
        if 'qwen' in model_name:
            # 如果是 Qwen 模型，则使用 OpenRouter 的配置
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("错误：环境变量 OPENROUTER_API_KEY 未设置。")
            
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            # 准备 OpenRouter 可能需要的额外请求头
            extra_args['extra_headers'] = {
                # "HTTP-Referer": "<YOUR_SITE_URL>", 
                # "X-Title": "<YOUR_SITE_NAME>",
            }
        else:
            # 否则，使用默认的 OpenAI 配置
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("错误：环境变量 OPENAI_API_KEY 未设置。")
            
            client = OpenAI(api_key=api_key)

        # 组织 message 消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 判断 user_prompt 类型，兼容原来的写法
        if isinstance(user_prompt, dict) and "content" in user_prompt:
            messages.append({"role": "user", "content": user_prompt["content"]})
        else:
            messages.append({"role": "user", "content": user_prompt})

        # 使用动态创建的 client 进行 OpenAI SDK 推理
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.0,
            max_tokens=512 if model_name in ['gpt-4o-mini', 'gpt-3.5-turbo'] else 256,
            **extra_args  # 将额外参数（如 extra_headers）解包传入
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