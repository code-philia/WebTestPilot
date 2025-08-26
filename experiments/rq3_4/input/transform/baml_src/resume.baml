class TransformedOutput {
  output string
}

function AddNoise(description: string) -> TransformedOutput {
  client "Qwen72b"
  prompt #"
    You are a web quality assurance expert.

    Add realistic syntactic noise to the text. 
    - Introduce casual imperfections such as typos, misspellings, redundant or repeated phrases, unnecessary filler words, or informal language. 
    - The goal is to simulate instructions written casually or imperfectly, while keeping the meaning mostly understandable.
    - You can also add filler words in a sentence that are relevant to the project but not the test itself.
    - Maintain the original meaning and intent of the test steps.

    {{ description }}

    {{ ctx.output_format }}
  "#
}

function Summarize(description: string) -> TransformedOutput {
  client "Qwen72b"
  prompt #"
    You are a web quality assurance expert.

    Summarize the test description below in a brief, concise format.
    - Assume that your reader is also a QA tester.
    - Assume that this is for internal use only.
    - Make it look like a very rough draft.
    - You can use abbreviations and short forms as needed.
    - Maintain the original meaning and intent of the test steps.

    {{ description }}

    {{ ctx.output_format }}
  "#
}

function Restyle(description: string) -> TransformedOutput {
  client "Qwen72b"
  prompt #"
    Rewrite the following test description so that each sentence may use a different documentation style. 
    - You can mix styles such as descriptive/expository, procedural/instructional, reference/technical, explanatory/conceptual, troubleshooting/problem-solving, narrative/storytelling, or casual/noisy.
    - Vary the style sentence by sentence.
    - Maintain the original meaning and intent of the test steps.

    {{ description }}

    {{ ctx.output_format }}
  "#
}