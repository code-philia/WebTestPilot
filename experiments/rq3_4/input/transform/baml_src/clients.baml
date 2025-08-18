client<llm> Qwen {
  provider "openai-generic"
  options {
    base_url "http://localhost:8000/v1"
    model "Qwen/Qwen2.5-VL-72B-Instruct-AWQ"
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