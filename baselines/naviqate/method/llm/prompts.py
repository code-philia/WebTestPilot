
abstract_to_concrete_prompt = """
We are using a web navigation agent to do a given task on a given website. Your task is to generate a concrete definition for a given abstracted task definition of a user scenario in that website.
You are provided with the following:
* Abstracted Task: The given task that you should generate the concrete description for it.
* Website: The given website that the generated task should be performed on.
* Description: meta description of the website.
* Examples: A numbered list of three similar abstracted tasks with their concrete equivalents. You can use these examples to better make your response.

Constraints:
* Your response should only be one sentence, describing the user task.
* You should generate required inputs, such as names, addresses, and numbers for the user task such that it could be executed by an automated web agent.
""".strip()

context_extraction_prompt = """
Your task is to explain the context of a webpage based on the provided information.
You will be provided with the following:
* description: meta description of the website,
* previous_state: context of the previous state (if there is any),
* previous_action: previous action that got us to this state (if there is any)

I need you to explain the context as abstractly as possible. Explain what the page is intended for mainly. Please use the following format for generating the response:
{
	“context”: String, // should be short and concise, without referring to anything specific
	“sub_functionalities”: list[String] // each functionality should be described in a single sentence
}
Examples 1:
{
	“context”: “This page is the landing page for a blog”,
	“sub_functionalities”: [
		“users can select different blog posts”,
		“users can navigate to pages such as about and home”
	]
}
Example 2:
{
	“context”: “This page shows the results for searching on an e-commerce website”,
	“sub_functionalities”: [
		“users can navigate to different parts of the website”,
		“users can select different products”,
		“users can change different parameters to filter the displayed products”
	]
}
Please make sure refrain from including any specific variables e.g. if the page shows the results for searching for a TV, do not mention anything about TVs, but refer to them with a more abstract term, such as products. Do this unless mentioning the variable name is absolutely necessary for understanding the page.
Please make sure your response is parsable by json.loads.
""".strip()


next_step_prompt = """
You are a web agent that uses Selenium to navigate a website and do a given task.
Your task is to predict the immediate next action that you should take to test a functionality (task) on a website. 
The action should not be typing the whole task in a search bar.
You will be provided with the following:
* task: A description of the functionality that needs to be tested.
* history: A list of previous actions (steps)
* context: A description of the current webpage.

Output Format:
Return a single, concise sentence instructing the user on the next immediate action to take or "Done". The sentence should:
* Start with either "Click" or "Type" (depending on the required action).
* Specify the target element.
* Given the history, if the task is complete, return "Done". 

Constraints:
* Do not suggest searching for the whole task description.
Do not suggest the following actions:
* Logging into an account
* Filling out credit card information
* Modifying cookie settings
""".strip()

which_actionable_prompt = """
You are a web agent that uses Selenium to navigate a website and do a given task.
You are to determine the most appropriate next action a user should perform to do the task.
Ensure that you replace 'random' or 'specific' or 'particular' with a suitable input, like number, location, name, etc. 
The "type" action is only for "input" elements.
Do not write the whole task in a search bar.
You will receive the following information:
* website
* task: A clear description of the user's objective.
* next step: A possible description of what the next action could be.
* history: A list of previous actions
* list of actionable elements: An array of actionables, each with a description and the element's tag name.
* a screenshot of the current webpage with a red label with yellow background showing the index for each actionable element.

Output Format:
Your output should consist of a JSON response with the following format:
	{
		"index": index_of_the_matching_action,
		"action": "click" | "type" | "select",
		"arg": value_to_be_typed_or_index_of_option_to_be_selected (if applicable)
	}
Constraints:
* Do not return anything other than a JSON response. Do not explain your answer.
""".strip()


element_functionality_prompt_with_context = """
Your task is to write a sentence describing the functionality of every item of a list of HTML elements given the text of its neighbours.
* Focus on the elements' functionality, not its appearance or style.
* The descriptions should be concise and in a single sentence.
* Your response should be a JSON object containing a list of descriptions. The keys of this JSON list are the indices.
""".strip()


dataset_abstraction_prompt = """
Your task is to convert specific user-defined tasks into a generalized abstract version. The abstract version should not contain specific user inputs but should instead describe the broader category of the task.

Sample Input:
Book a table for two at an Italian restaurant in New York City

Sample Output:
Make a reservation at a specific type of restaurant in a city
""".strip()
