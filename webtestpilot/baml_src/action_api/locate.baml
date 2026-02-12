function LocateUIElement(screenshot: image, description: string) -> string {
  client "Base"
  prompt #"
    {{_.role("user")}}
    Outline the position corresponding to the instruction: {{description}}. The output should be only [x1,y1,x2,y2].
    {{ screenshot }}
  "#
}