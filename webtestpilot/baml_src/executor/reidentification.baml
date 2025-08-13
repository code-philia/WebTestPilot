class PageAbstract {
  name string
  description string
  layout string
}


function IsSameLogicalPage(page_a: image, page_b: image) -> bool {
  client "GPT"
  prompt #"
    {{_.role("user")}}
    You are an expert UI/UX evaluator with deep knowledge of web page layout, semantics, and interaction patterns.

    You are given two page screenshots. Determine whether they represent the same logical page 
    (i.e., the same underlying page in a web application or site), even if their visual states differ.

    Guidelines:
    1. Layout Consistency: Do the overall structure and arrangement of UI components match?

    2. Functional Equivalence: Do they offer the same set of core actions and interactions?

    3. Navigation Equivalence: Do they provide the same pathways to other parts of the application?

    4. Two pages can be the same, even if their visual states differ. For example:
        - One shows an expanded/triggered widget (e.g., dropdown, modal, accordion, pop-up).
        - One contains different dynamic data but with the same type, structure, and placement.
        - One has pre-filled or empty form fields, as long as the underlying form is the same.

    {{ ctx.output_format }}

    {{ page_a }}

    {{ page_b}}
  "#
}


function AbstractPage(page: image) -> PageAbstract {
  client "GPT"
  prompt #"
    {{_.role("user")}}
    You are an expert UI/UX evaluator with deep knowledge of web page layout, semantics, and interaction patterns.
    
    You are given a page screenshot.
    1. Assign a clear, semantically meaningful name to the page (e.g., Shopping Cart Page).
    2. Write a summary <15 words describing both the function and visual state of the page.
    3. Analyze the layout: extract as a page template in XML format. You may include non-data attributes for context.
      ```example
      <Page>
        <Header visibleFor="allUsers" role="navigation" hasNotifications="true" />
        <Sidebar collapsible="true" visible="true" contains="menuItems" />
        <Breadcrumb currentPage="true" hasPath="true" />
        <MainContent>
          <CartItems type="list" itemType="product" selectable="true" hasQuantity="true" hasPrice="true" availabilityState="enum" />
          <Recommendations type="list" itemType="product" algorithmType="collaborativeFiltering" />
        </MainContent>
        <Footer role="footer" contains="links,contactInfo" />
      </Page>
      ```

    {{ ctx.output_format }}

    {{ page }}
  "#
}

test TestName {
  functions [AbstractPage]
  args {
    page { file "/home/xiwen/WebTestPilot/webtestpilot/baml_src/executor/invoiceninja.png" }
  }
}