template_string API_Specification() #"
    # API Specification

    ### Session API
    - `history -> list[State]`: Chronological sequence of all captured states in the current test session.

    ### State API
    - `page_id -> str`: Canonical identifier for logical page/state identity.
    - `title -> str`: Browser tab title, not the visible page heading. Do not use this to verify page content such as "Your account"; extract visible headings/page content from the latest state instead.
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
      - If you need a list of items, wrap it in a container model and iterate over the list field. Do NOT pass a singular item model and then iterate over the returned model.
        Correct:
        ```python
        class Product(BaseModel):
            title: str
        class ProductList(BaseModel):
            items: List[Product] = Field(default_factory=list)
        products = state.extract("get products", schema=ProductList).items
        ```
      - Do NOT use `dict`, `List[dict]`, or untyped mappings for extracted objects. Define a nested `BaseModel` for each structured item so attributes can be accessed safely.
      - Keep fields used in assertions at the same object level where they are declared. For example, do not assert `item.quantity` unless `quantity` is declared on `CartItem`; if it is declared on `Product`, assert `item.product.quantity`.
      - If a field may be absent because a dialog or message is not visible, declare it as Optional with a default, e.g. `title: Optional[str] = None`, then assert on the value.
      - When comparing human-visible text such as product titles, headings, and labels, normalize whitespace and case unless the expectation explicitly requires exact capitalization.
      - The extractor will populate and return an instance of the provided subclass (or data matching its schema). Provide only class objects, not instances or the `BaseModel` base class.
      - If you provide a schema that is not a subclass of `BaseModel` or omits required fields, extraction will fail. Ensure the schema accurately reflects the structure you expect to extract from the state.

    Examples:
    - Correct: `extract("get user", schema=User)` where `User` inherits from `BaseModel`.
    - Incorrect: `extract("get user", schema=BaseModel)` (do not pass the base type).
"#
