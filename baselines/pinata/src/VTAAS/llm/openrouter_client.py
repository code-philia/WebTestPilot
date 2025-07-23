import ast
import base64
from collections.abc import Iterable
from copy import deepcopy
import json
import logging
import os
import time
from typing import final, override
from uuid import uuid4

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from openai import OpenAIError, AsyncOpenAI
from pydantic import BaseModel

from VTAAS.llm.llm_client import LLMClient


from ..schemas.llm import (
    Message,
    MessageRole,
    LLMActResponse,
    LLMAssertResponse,
    LLMDataExtractionResponse,
    LLMTestStepFollowUpResponse,
    LLMTestStepPlanResponse,
    LLMTestStepRecoverResponse,
)

from ..utils.logger import get_logger
from ..utils.config import load_config
import sys


@final
class OpenRouterLLMClient(LLMClient):
    """Communication with OpenRouter through the OpenAI API client"""

    def __init__(
        self,
        name: str,
        start_time: float,
        output_folder: str,
        model: str = "meta-llama/llama-3.2-90b-vision-instruct",
    ):
        load_config()
        self.start_time = start_time
        self.output_folder = output_folder
        self.model = model
        self.name: str = name
        self.logger = get_logger(
            "OpenRouter LLM Client - " + self.name + " - " + uuid4().hex,
            self.start_time,
            self.output_folder,
        )
        self.logger.setLevel(logging.DEBUG)
        self.max_tries = 3
        try:
            self.aclient = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
        except OpenAIError as e:
            self.logger.fatal(e, exc_info=True)
            sys.exit(1)

    @override
    async def plan_step(self, conversation: list[Message]) -> LLMTestStepPlanResponse:
        """Get list of act/assert workers from LLM."""
        attempts = 1
        while attempts <= self.max_tries:
            try:
                self.logger.debug(
                    f"Init Plan Step Message:\n{conversation[-1].content}"
                )
                response = await self.aclient.beta.chat.completions.parse(
                    model=self.model,
                    messages=self._to_openai_messages(conversation),
                    temperature=0,
                    seed=192837465,
                    frequency_penalty=0.7,
                    response_format=LLMTestStepPlanResponse,
                    # extra_body={"provider": {"require_parameters": True}},
                    extra_body={
                        "provider": {"ignore": ["SambaNova", "DeepInfra", "Together"]}
                    },
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan step call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                llm_response = LLMTestStepPlanResponse.model_validate(
                    ast.literal_eval(response.choices[0].message.content or "")
                )
                self.logger.info(
                    f"Orchestrator Plan response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan step parsing: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
        raise Exception("could not send Step planning request")

    @override
    async def followup_step(
        self, conversation: list[Message]
    ) -> LLMTestStepFollowUpResponse:
        """Update list of act/assert workers from LLM."""
        attempts = 1
        while attempts <= self.max_tries:
            try:
                self.logger.debug(
                    f"FollowUp Plan Step Message:\n{conversation[-1].content}"
                )
                response = await self.aclient.beta.chat.completions.parse(
                    model=self.model,
                    messages=self._to_openai_messages(conversation),
                    temperature=0,
                    seed=192837465,
                    frequency_penalty=0.7,
                    extra_body={
                        "provider": {"ignore": ["SambaNova", "DeepInfra", "Together"]}
                    },
                    response_format=LLMTestStepFollowUpResponse,
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan followup call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                llm_response = LLMTestStepFollowUpResponse.model_validate(
                    ast.literal_eval(response.choices[0].message.content or "")
                )
                self.logger.info(
                    f"Orchestrator Follow-Up response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.error(
                    f"Error #{attempts} in plan followup parsing: {str(e)}"
                )
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
        raise Exception("could not send step planning followup request")

    @override
    async def recover_step(
        self, conversation: list[Message]
    ) -> LLMTestStepRecoverResponse:
        """Update list of act/assert workers from LLM."""
        attempts = 1
        while attempts <= self.max_tries:
            try:
                self.logger.debug(f"Recover Step Message:\n{conversation[-1].content}")
                response = await self.aclient.beta.chat.completions.parse(
                    model=self.model,
                    messages=self._to_openai_messages(conversation),
                    temperature=0,
                    seed=192837465,
                    frequency_penalty=0.7,
                    extra_body={
                        "provider": {"ignore": ["SambaNova", "DeepInfra", "Together"]}
                    },
                    response_format=LLMTestStepRecoverResponse,
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan recover call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if not response.choices[0].message.content:
                    raise Exception("LLM response is empty")
                llm_response = LLMTestStepRecoverResponse.model_validate(
                    ast.literal_eval(response.choices[0].message.content or "")
                )
                self.logger.info(
                    f"Orchestrator Recover response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.error(
                    f"Error #{attempts} in plan recover parsing: {str(e)}"
                )
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
        raise Exception("could not send Step planning recover request")

    @override
    async def act(self, conversation: list[Message]) -> LLMActResponse:
        """Actor call"""
        attempts = 1
        while attempts <= self.max_tries:
            try:
                self.logger.debug(f"Actor User Message:\n{conversation[-1].content}")
                response = await self.aclient.beta.chat.completions.parse(
                    model=self.model,
                    messages=self._to_openai_messages(conversation),
                    temperature=0,
                    seed=192837465,
                    frequency_penalty=0.7,
                    extra_body={
                        "provider": {"ignore": ["SambaNova", "DeepInfra", "Together"]}
                    },
                    response_format=LLMActResponse,
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in act call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if not response.choices[0].message.content:
                    raise Exception("LLM response is empty")
                llm_response = LLMActResponse.model_validate(
                    ast.literal_eval(response.choices[0].message.content or "")
                )
                self.logger.info(
                    f"Actor response {llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.error(f"Error #{attempts} in act parsing: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
        raise Exception("could not send Act request")

    @override
    async def assert_(self, conversation: list[Message]) -> LLMAssertResponse:
        """Assertor call"""
        attempts = 1
        error_suffix = ""
        self.logger.debug(f"Assertor User Message:\n{conversation[-1].content}")
        while attempts <= self.max_tries:
            convo = deepcopy(conversation)
            convo[-1].content += error_suffix
            expected_format = OpenRouterLLMClient.generate_prompt_from_pydantic(
                LLMDataExtractionResponse
            )
            conversation[-1].content += expected_format
            try:
                response = await self.aclient.beta.chat.completions.parse(
                    model=self.model,
                    messages=self._to_openai_messages(convo),
                    temperature=0
                    + (
                        0.2 * (attempts - 1)
                    ),  # We increase the temp with the failures to expect a different output
                    seed=192837465,
                    frequency_penalty=0.7,
                    extra_body={
                        "provider": {"ignore": ["SambaNova", "DeepInfra", "Together"]}
                    },
                    response_format=LLMAssertResponse,
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in assert call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if not response.choices[0].message.content:
                    raise Exception("LLM response is empty")
                llm_response = LLMAssertResponse.model_validate(
                    ast.literal_eval(response.choices[0].message.content or "")
                )
                self.logger.info(
                    f"Assertor response {llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.error(f"Error #{attempts} in assert parsing: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                error_suffix = (
                    "\nNote that your last answer could not be parsed by pydantic:"
                    f"\n{str(e)}\nPlease ensure you respect the provided response schema. "
                    "In case of a failed status, make sure to explicitely mention the finish command."
                )
                attempts += 1
                continue
        raise Exception("could not send Assert request")

    @override
    async def step_postprocess(
        self, system: str, user: str, screenshots: list[bytes]
    ) -> LLMDataExtractionResponse:
        """Data Extraction call"""
        attempts = 1
        while attempts <= self.max_tries:
            conversation: list[Message] = [
                Message(role=MessageRole.System, content=system),
                Message(
                    role=MessageRole.User,
                    content=user,
                    screenshot=screenshots,
                ),
            ]
            try:
                response = await self.aclient.beta.chat.completions.parse(
                    model=self.model,
                    messages=self._to_openai_messages(conversation),
                    temperature=0,
                    seed=192837465,
                    frequency_penalty=0.7,
                    extra_body={
                        "provider": {"ignore": ["SambaNova", "DeepInfra", "Together"]}
                    },
                    response_format=LLMDataExtractionResponse,
                )
            except Exception as e:
                self.logger.error(
                    f"Error #{attempts} in data extraction call: {str(e)}"
                )
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                resp_msg = response.choices[0].message.content
                if not resp_msg:
                    raise Exception("Data Extraction response is empty")
                llm_response = LLMDataExtractionResponse.model_validate(
                    ast.literal_eval(response.choices[0].message.content or "")
                )

                self.logger.info(
                    f"Data extraction response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.error(
                    f"Error #{attempts} in data extraction parsing: {str(e)}"
                )
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
        raise Exception("could not send Data extraction request")

    @staticmethod
    def generate_prompt_from_pydantic(model: type[BaseModel]) -> str:
        """
        Anthropic does not support structured outputs. Let's ask the model to adhere to the format in the prompt
        """
        schema = model.model_json_schema()
        prompt = (
            "\nYour response must be a json.loads parsable JSON object, following this Pydantic JSON schema:\n"
            f"{json.dumps(schema, indent=2)}"
            "\n please omit properties that have a default null if you don't plan on valuing them"
        )
        return prompt

    @staticmethod
    def extract_json(response: str) -> str:
        json_start = response.index("{")
        json_end = response.rfind("}")
        return response[json_start : json_end + 1]

    def _to_openai_messages(
        self, conversation: list[Message]
    ) -> Iterable[ChatCompletionMessageParam]:
        messages: Iterable[ChatCompletionMessageParam] = []
        for msg in conversation:
            match msg.role:
                case MessageRole.System:
                    messages.append(
                        ChatCompletionSystemMessageParam(
                            role="system", content=msg.content
                        )
                    )
                case MessageRole.Assistant:
                    messages.append(
                        ChatCompletionAssistantMessageParam(
                            role="assistant", content=msg.content
                        )
                    )
                case MessageRole.User:
                    content: Iterable[ChatCompletionContentPartParam] = []
                    content.append(
                        ChatCompletionContentPartTextParam(
                            type="text", text=msg.content
                        )
                    )
                    if msg.screenshot:
                        for screenshot in msg.screenshot:
                            base64_screenshot = str(
                                base64.b64encode(screenshot), "utf-8"
                            )
                            image = ImageURL(
                                url=f"data:image/png;base64,{base64_screenshot}",
                                detail="high",
                            )
                            content.append(
                                ChatCompletionContentPartImageParam(
                                    image_url=image, type="image_url"
                                )
                            )
                    messages.append(
                        ChatCompletionUserMessageParam(content=content, role="user")
                    )
        return messages
