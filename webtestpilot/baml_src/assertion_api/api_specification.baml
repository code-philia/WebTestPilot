template_string API_Specification() #"
    # API Specification

    ### Session API
    - `history -> list[State]`: Chronological sequence of all captured states in the current test session.

    ### State API
    - `page_id -> str`: Canonical identifier for logical page/state identity.
    - `title -> str`: Browser tab's visible title.
    - `url -> str`: Current browser URL.
    - `extract(instruction: str, schema: Type[BaseModel]) -> Type[BaseModel]`: Extract structured data from the state. `schema` should be a class inherited from `BaseModel`, NOT `BaseModel` itself.

    Important requirements for `schema`:
      - `schema` must be a concrete subclass of `BaseModel` (a class that inherits from `BaseModel` and defines fields). Do NOT pass `BaseModel` itself.
      - The subclass should declare the expected fields and their types. Example:
        ```python
        class User(BaseModel):
            id: int
            name: str
        ```
      - The extractor will populate and return an instance of the provided subclass (or data matching its schema). Provide only class objects, not instances or the `BaseModel` base class.
      - If you provide a schema that is not a subclass of `BaseModel` or omits required fields, extraction will fail. Ensure the schema accurately reflects the structure you expect to extract from the state.

    Examples:
    - Correct: `extract("get user", schema=User)` where `User` inherits from `BaseModel`.
    - Incorrect: `extract("get user", schema=BaseModel)` (do not pass the base type).
"#