class Output {
    @@dynamic
}

type Primitives = string | int | float | bool
type ExtractedData = Output | Primitives | Output[] | Primitives[]


function ExtractFromState(screenshot: image, instruction: string) -> Output {
    client "Base"
    prompt #"
        {{_.role("user")}}
        Extract structured data from the webpage screenshot that is relevant to the instruction.

        {{ screenshot }}

        Instruction: {{ instruction }}

        {{ ctx.output_format }}
    "#
}

function ExtractFromElement(screenshot: image, html: string, instruction: string) -> Output {
    client "Base"
    prompt #"
        {{_.role("user")}}
        Extract structured data from the web UI element screenshot and HTML that is relevant to the instruction.

        {{ screenshot }}

        {{ html }}

        Instruction: {{ instruction }}

        {{ ctx.output_format }}
    "#
}