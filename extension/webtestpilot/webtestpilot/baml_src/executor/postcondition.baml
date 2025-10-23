template_string PostconditionIntro() #"
    # Role
    You are an expert QA tester.

    # Objective
    You are generating a **postcondition assertion** after a specific user action has been executed.
    Your goal is to verify that the intended **effects** of the action have occurred.

    # Instructions
    - Construct a Python assertion function using the provided Session, State, and Element APIs as detailed below.
    - Focus on **postcondition verification**: ensure the *intended outcome* is reflected in the state after the action.
    - Identify which dependency types are relevant to the state change:
        1. **Temporal Dependency:** Changes in a logical page over time (e.g., after an action, a formerly empty cart now has items).
        2. **Data Dependency:** Propagation of information across states (e.g., product details remain consistent from search result to cart addition).
        3. **Causal Dependency:** State changes resulting directly from user actions (e.g., clicking 'search' updates the page to show related items).
    - Grounding: Use only information provided in the session or state. Do not invent or guess labels, text, or values.
    - Prefer structural checks (e.g., count > 0, len >= N, is not None) when exact expected values are not known.
    - No placeholders. Even if expectations are minimal.

    - Write the assertion as a Python block:
        ```python
        def position(session: Session):
            ...
        ```
"#

template_string PostconditionExample() #"
    # Example
    __input__
    History:
        State (0): 
            Page: Cart page; 
            Action: User clicks "Continue Shopping"
        ...
        State (4): 
            Page: Product detail view
            Action: User adds the item to cart

    Current: Cart page (After action) 
    Assert: Cart is correctly updated

    __output__
    ```python
    def postcondition(session: Session):
        # Define data models
        class Product(BaseModel): 
            title: str = Field(..., description="The name of the product")
            price: float = Field(..., description="The unit price of the product in local currency")
            quantity: Optional[int] = Field(None, "The quantity of this product (used in cart contexts). None indicates unlimited or not specified")
        
        class Cart(BaseModel): 
            items: List[Product] = Field(default_factory=list, description="List of products in the cart with their respective quantities")

        # Extract product from latest state
        added = session.history[-2].extract("get product detail", schema=Product)

        # Get current and prior cart items
        current = session.history[-1].extract("get cart summary", schema=Cart).items
        prior = session.history[0].extract("get cart summary", schema=Cart).items

        # Assert cart contains prior items plus the added product
        assert set(p.title for p in current) == set(p.title for p in prior + [added])
    ```
"#

function GeneratePostcondition(screenshot: image, history: History[], action: string, verify: string, feedback: Feedback[]) -> string {
    client "Base"
    prompt #"
        {{_.role("user")}}
        {{ PostconditionIntro() }}

        {{ Specification() }}

        {{ PostconditionExample() }}
        
        {{ screenshot }}

        {{ FormatHistory(history) }}
        After Action: {{ action }}
        Assert: {{ verify }}
        {{ FormatFeedback(feedback) }}
    "#
}


test TestName {
  functions [GeneratePostcondition]
  args {
    verify #"
      hello world
    "#
    history [
        {
            page_id "A"
        }
    ]
    feedback [
        {
            response "test"
            reason "test"
        }
    ]
    screenshot { url "https://imgs.xkcd.com/comics/standards.png" }
  }
}
