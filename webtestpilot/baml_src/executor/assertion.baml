function GenerateAssertion(verify: string, history: string, screenshot: image) -> string {
    client "GPT"
    prompt #"
        {{_.role("user")}}
        # Role
        You are an expert QA tester skilled at writing concise, robust Python test assertions.

        # Objective
        Write a Python assertion function (see format below) for a web interaction using session history and reasoning about states, elements, and actions. The assertion must:
        
        # Instructions
        - Construct a Python assertion function for a web interaction scenario using only the provided Session, State, and Element APIs as detailed below.
        - Identify and leverage three types of dependencies between previous and current browser states:
            1. **Temporal Dependency:** Changes in a logical page over time (e.g., after an action, a formerly empty cart now has items).
            2. **Data Dependency:** Propagation of information across states (e.g., product details remain consistent from search result to cart addition).
            3. **Causal Dependency:** State changes resulting directly from user actions (e.g., clicking 'search' updates the page to show related items).

        - Select relevant browser states and elements to trace key transitions that align with the expected outcome.
        - Write the assertion as a Python block:
            ```python
            def assertion(session: Session):
                ...
            ```

        # API Specification

        ### Session API
        - `history -> list[State]`: Chronological sequence of all captured states in the current test session.
        - `state -> State`: Access the active browser page's state.

        ### State API
        - `page_id -> str`: Canonical identifier for logical page/state identity.
        - `title -> str`: Browser tab's visible title.
        - `url -> str`: Current browser URL.
        - `extract(instruction: str, schema: BaseModel) -> dict`: Extract structured data from the state.
        - `get_element(description: str) -> Element`: Obtain an Element object via visual description.

        ### Element API
        - `extract(instruction: str, schema: BaseModel) -> dict`: Extract structured data from the element.

        # Example
        __input__
        History:
            State (0): Cart page; cart is empty; action: User clicks "Continue Shopping"
            State (1): Homepage; action: User enters the query "camera" in the search bar
            State (2): Search field focused; action: Search suggestions appear
            State (3): Search results page; action: User clicks 'Search'; results are displayed
            State (4): Product detail view; action: User adds the item to cart

        Current: Cart page

        Assert: Cart is correctly updated

        __output__
        ```python
        def assertion(session: Session):
            # Define data models
            class Product(BaseModel): title: str; price: float; quantity: Optional[int]
            class Cart(BaseModel): items: List[Product]

            # Extract product from latest state
            added = session.history[-1].extract("get product detail", schema=Product)

            # Get current and prior cart items
            current = session.state.extract("get cart summary", schema=Cart).items
            prior = session.history[-2].extract("get cart summary", schema=Cart).items

            # Assert cart contains prior items plus the added product
            assert set(p.title for p in current) == set(p.title for p in prior + [added])
        ```

        {{ screenshot }}

        {{ history }}

        {{ verify }}
    "#
}

test InvoiceNinja {
  functions [GenerateAssertion]
  args {
    verify #"
        Assertion: Client changes are saved
    "#
    history #"
        History:
            State (0): Clients Page; Navigate to the client created in TC-002
            State (1): Client Details Page; Click "Edit" button or link
            State (2): Client Edit Page; Click in the "Name" textbox
            State (3): Client Edit Page; Clear the name field and type "company_name Updated 123456"
            State (4): Client Edit Page; Click "Save" button
        
        Current: Clients Page
    "#
    screenshot { file "./invoiceninja.png" }
  }
}
