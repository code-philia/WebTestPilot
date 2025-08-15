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
    model "gpt-4.1"
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

client<llm> Qwen {
  provider "openai-generic"
  options {
    base_url "https://localhost:8000/v1"
    model "Qwen/Qwen2.5-VL-72B-Instruct-AWQ"
  }
}

client<llm> InternVL {
  provider "openai-generic"
  options {
    base_url "https://localhost:8000/v1"
    model "OpenGVLab/InternVL3-38B-AWQ"
  }
}

client<llm> UITARS {
  provider "openai-generic"
  options {
    base_url "https://localhost:8000/v1"
    model "ByteDance-Seed/UI-TARS-72B-DPO"
  }
}

client<llm> UGround {
  provider "openai-generic"
  options {
    base_url "http://echo-dongjs.ddns.comp.nus.edu.sg:8000/v1"
    api_key "token-abc123"
    model "osunlp/UGround-V1-7B"
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