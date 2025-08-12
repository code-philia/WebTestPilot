class Output {
    @@dynamic
}

function Extract(screenshot: image, description: string) -> Output {
    client "GPT"
    prompt #"
        {{_.role("user")}}
        Extract structured data from the webpage screenshot that is relevant to the objective.

        {{ screenshot }}

        Objective: {{ description }}

        {{ ctx.output_format }}
    "#
}