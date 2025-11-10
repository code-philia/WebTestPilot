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
    model "gpt-4o-mini"
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

client<llm> OpenRouter {
  provider "openai-generic"
  options {
    base_url "https://openrouter.ai/api/v1"
    model "openai/gpt-oss-120b"
    api_key env.OPENROUTER_API_KEY
  }
}

client<llm> ZrokLocalModel {
  provider "openai-generic"
  retry_policy Exponential
  options {
    base_url "https://llms.zrok.06946099.xyz/v1"
    model "Qwen/Qwen3-VL-30B-A3B-Thinking"
    temperature 0.0
  }
}

client<llm> NgrokLocalModel {
  provider "openai-generic"
  retry_policy Exponential
  options {
    base_url "https://viperish-fawn-superhumanly.ngrok-free.dev/v1"
    model "Qwen/Qwen3-VL-30B-A3B-Thinking"
    temperature 0.0
  }
}

client<llm> FallbackLocalModel {
  provider fallback
  options {
    strategy [
      GPT
      OpenRouter
      ZrokLocalModel
      NgrokLocalModel
    ]
  }
}

client<llm> ZrokUIVenus {
  provider "openai-generic"
  retry_policy Exponential
  options {
    base_url "https://uivenus.zrok.06946099.xyz/v1"
    api_key "token-abc123"
    model "inclusionAI/UI-Venus-Ground-7B"
    temperature 0.0
    header {
      "secret" "sjtu-course-cs3604-2025"
    }
  }
}

client<llm> ZrokUIVenus2 {
  provider "openai-generic"
  retry_policy Exponential
  options {
    base_url "https://uivenus2.zrok.06946099.xyz/v1"
    api_key "token-abc123"
    model "inclusionAI/UI-Venus-Ground-7B"
    temperature 0.0
    header {
      "secret" "sjtu-course-cs3604-2025"
    }
  }
}

client<llm> NgrokUIVenus {
  provider "openai-generic"
  retry_policy Exponential
  options {
    base_url "https://8dcd0b9d943d.ngrok-free.app/v1"
    api_key "token-abc123"
    model "inclusionAI/UI-Venus-Ground-7B"
    temperature 0.0
  }
}

client<llm> FallbackUIVenus1 {
  provider fallback
  options {
    strategy [
      ZrokUIVenus
      ZrokUIVenus2
      NgrokUIVenus
    ]
  }
}

client<llm> FallbackUIVenus2 {
  provider fallback
  options {
    strategy [
      ZrokUIVenus2
      ZrokUIVenus
      NgrokUIVenus
    ]
  }
}

client<llm> UIVenusRoundRobin {
  provider round-robin
  options {
    strategy [
      FallbackUIVenus1
      FallbackUIVenus2
    ]
  }
}

retry_policy Exponential {
  max_retries 5
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 50000
  }
}
