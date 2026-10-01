client<llm> Transform {
  provider "openai-generic"
  options {
    base_url env.TRANSFORM_MODEL_BASE_URL
    model env.TRANSFORM_MODEL_NAME
    temperature 0.0
  }
}