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
    base_url env.OPENAI_BASE_URL
    model env.OPENAI_MODEL_NAME
    api_key env.OPENAI_API_KEY
    temperature 0.0
  }
}

client<llm> Gemini {
  provider google-ai
  retry_policy Exponential
  options {
    model env.GOOGLEAI_MODEL_NAME
    api_key env.GOOGLEAI_API_KEY
    temperature 0.0
  }
}

client<llm> Claude {
  provider anthropic
  retry_policy Exponential
  options {
    model env.ANTHROPIC_MODEL_NAME
    api_key env.ANTHROPIC_API_KEY
    temperature 0.0
  }
}

client<llm> Local {
  provider "openai-generic"
  options {
    base_url env.LOCAL_MODEL_BASE_URL
    model env.LOCAL_MODEL_NAME
    temperature 0.0
  }
}

client<llm> GUI_Grounding_Model {
  provider "openai-generic"
  options {
    base_url env.GUI_GROUNDING_MODEL_BASE_URL
    model env.GUI_GROUNDING_MODEL_NAME
    temperature 0.0
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
