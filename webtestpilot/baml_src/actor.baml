function LocateUIElement(screenshot: image, description: string) -> string {
  client "UGround"
  prompt #"
    {{_.role("user")}}

    {{ screenshot }}

    Your task is to help the user identify the precise coordinates (x, y) of a specific area/element/object on the screen based on a description.

    - Your response should aim to point to the center or a representative point within the described area/element/object as accurately as possible.
    - If the description is unclear or ambiguous, infer the most relevant area or element based on its likely context or purpose.
    - Your answer should be a single string (x, y) corresponding to the point of the interest.

    Description: {{ description }}

    Answer:
  "#
}