// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

// This is a stub client definition.
// Actual provider clients (with real implementations) are selected and
// instantiated at runtime based on the config/env
client<llm> Base {
  provider "openai-generic"
  options {
    base_url ""
  }
}

client<llm> GPT {
  provider openai
  retry_policy Exponential
  options {
    model "gpt-4.1-mini"
    api_key env.OPENAI_API_KEY
    temperature 0.0
  }
}

client<llm> Gemini {
  provider google-ai
  retry_policy Exponential
  options {
    model "gemini-2.5-pro"
    api_key env.GOOGLEAI_API_KEY
  }
}

client<llm> Claude {
  provider anthropic
  retry_policy Exponential
  options {
    model "claude-sonnet-4-20250514"
    api_key env.ANTHROPIC_API_KEY
  }
}

client<llm> Qwen72b {
  provider "openai-generic"
  options {
    base_url "http://localhost:8000/v1"
    model "Qwen/Qwen2.5-VL-72B-Instruct-AWQ"
  }
}

client<llm> Qwen32b {
  provider "openai-generic"
  options {
    base_url "http://localhost:8000/v1"
    model "Qwen/Qwen2.5-VL-32B-Instruct-AWQ"
  }
}

client<llm> Qwen7b {
  provider "openai-generic"
  options {
    base_url "http://localhost:8000/v1"
    model "Qwen/Qwen2.5-VL-7B-Instruct-AWQ"
  }
}

client<llm> Qwen3b {
  provider "openai-generic"
  options {
    base_url "http://localhost:8000/v1"
    model "Qwen/Qwen2.5-VL-3B-Instruct-AWQ"
  }
}

client<llm> Qwen3VL2b {
  provider "openai-generic"
  options {
    base_url "https://viperish-fawn-superhumanly.ngrok-free.dev/v1"
    model "Qwen/Qwen3-VL-2B-Instruct"
  }
}

client<llm> OpenRouter {
  provider "openai-generic"
  options {
    base_url "https://openrouter.ai/api/v1"
    model "qwen/qwen2.5-vl-32b-instruct:free"
    api_key env.OPENROUTER_API_KEY
  }
}

client<llm> LocalModel {
  provider "openai-generic"
  options {
    // base_url "https://viperish-fawn-superhumanly.ngrok-free.dev/v1"
    base_url "https://dgh8bwp6wn5g.share.zrok.io/v1"
    model "Qwen/Qwen3-VL-30B-A3B-Thinking"
  }
}

client<llm> UIVenus {
  provider "openai-generic"
  options {
    base_url "https://24x723l6jtk1.share.zrok.io/v1"
    // base_url "https://7b45fdfd7206.ngrok-free.app/v1"
    // base_url "https://viperish-fawn-superhumanly.ngrok-free.dev/v1"
    api_key "token-abc123"
    model "inclusionAI/UI-Venus-Ground-7B"
  }
}

retry_policy Exponential {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}