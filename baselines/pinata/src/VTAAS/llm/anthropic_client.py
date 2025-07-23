import ast
import base64
from collections.abc import Iterable
import json
import time
from typing import final, override
from uuid import uuid4

from anthropic import AsyncAnthropic
from anthropic.types import TextBlock
from anthropic.types.image_block_param import ImageBlockParam, Source
from anthropic.types.message_param import MessageParam
from anthropic.types.text_block_param import TextBlockParam
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
class AnthropicLLMClient(LLMClient):
    """Communication with OpenAI"""

    def __init__(self, name: str, start_time: float, output_folder: str):
        load_config()
        self.start_time = start_time
        self.output_folder = output_folder
        self.name: str = name
        self.logger = get_logger(
            "Anthropic LLM Client - " + self.name + " - " + uuid4().hex,
            self.start_time,
            self.output_folder,
        )
        self.max_tries = 3
        try:
            self.aclient = AsyncAnthropic(max_retries=4)
        except Exception as e:
            self.logger.fatal(e, exc_info=True)
            sys.exit(1)

    @override
    async def plan_step(self, conversation: list[Message]) -> LLMTestStepPlanResponse:
        """Get list of act/assert workers from LLM."""
        attempts = 1
        self.logger.debug(f"Init Plan Step Message:\n{conversation[-1].content}")
        expected_format = AnthropicLLMClient.generate_prompt_from_pydantic(
            LLMTestStepPlanResponse
        )
        conversation[-1].content += expected_format
        preshot_assistant = Message(
            role=MessageRole.Assistant,
            content='{"',
        )
        conversation.append(preshot_assistant)
        while attempts <= self.max_tries:
            try:
                response = await self.aclient.messages.create(
                    max_tokens=1000,
                    model="claude-3-5-sonnet-latest",
                    temperature=0,
                    messages=AnthropicLLMClient.to_anthropic_messages(conversation),
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan step call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if len(response.content) == 0:
                    raise ValueError("PLAN - anthropic response is empty")
                outcome = response.content[0]
                if not isinstance(outcome, TextBlock):
                    raise ValueError("PLAN - anthropic response is not text")
                response_str = AnthropicLLMClient.extract_json('{"' + outcome.text)
                llm_response = LLMTestStepPlanResponse.model_validate(
                    ast.literal_eval(response_str)
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
        self.logger.debug(f"FollowUp Plan Step Message:\n{conversation[-1].content}")
        expected_format = AnthropicLLMClient.generate_prompt_from_pydantic(
            LLMTestStepFollowUpResponse
        )
        conversation[-1].content += expected_format
        preshot_assistant = Message(
            role=MessageRole.Assistant,
            content='{"',
        )
        conversation.append(preshot_assistant)
        while attempts <= self.max_tries:
            try:
                response = await self.aclient.messages.create(
                    max_tokens=1000,
                    model="claude-3-5-sonnet-latest",
                    messages=self.to_anthropic_messages(conversation),
                    temperature=0,
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan followup call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if len(response.content) == 0:
                    raise ValueError("FOLLOWUP - anthropic response is empty")
                outcome = response.content[0]
                if not isinstance(outcome, TextBlock):
                    raise ValueError("FOLLOWUP - anthropic response is not text")
                response_str = AnthropicLLMClient.extract_json('{"' + outcome.text)
                llm_response = LLMTestStepFollowUpResponse.model_validate(
                    ast.literal_eval(response_str or "")
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
        self.logger.debug(f"Recover Step Message:\n{conversation[-1].content}")
        expected_format = AnthropicLLMClient.generate_prompt_from_pydantic(
            LLMTestStepRecoverResponse
        )
        conversation[-1].content += expected_format
        preshot_assistant = Message(
            role=MessageRole.Assistant,
            content='{"',
        )
        conversation.append(preshot_assistant)
        while attempts <= self.max_tries:
            try:
                response = await self.aclient.messages.create(
                    max_tokens=1000,
                    model="claude-3-5-sonnet-latest",
                    messages=self.to_anthropic_messages(conversation),
                    temperature=0,
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan recover call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if len(response.content) == 0:
                    raise ValueError("RECOVER - anthropic response is empty")
                outcome = response.content[0]
                if not isinstance(outcome, TextBlock):
                    raise ValueError("RECOVER - anthropic response is not text")
                response_str = AnthropicLLMClient.extract_json('{"' + outcome.text)
                llm_response = LLMTestStepRecoverResponse.model_validate(
                    ast.literal_eval(response_str or "")
                )
                self.logger.info(
                    f"Orchestrator Recover response:\n{llm_response.model_dump_json(indent=4)}"
                )
                if llm_response.plan:
                    self.logger.info(
                        f"[Recover] Received {len(llm_response.plan.workers)} worker configurations from LLM"
                    )
                else:
                    self.logger.info("[Recover] Test step is considered FAIL")

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
        self.logger.debug(f"Actor User Message:\n{conversation[-1].content}")
        expected_format = AnthropicLLMClient.generate_prompt_from_pydantic(
            LLMActResponse
        )
        conversation[-1].content += expected_format
        preshot_assistant = Message(
            role=MessageRole.Assistant,
            content='{"',
        )
        conversation.append(preshot_assistant)
        while attempts <= self.max_tries:
            try:
                response = await self.aclient.messages.create(
                    max_tokens=1000,
                    model="claude-3-5-sonnet-latest",
                    messages=self.to_anthropic_messages(conversation),
                    temperature=0,
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in act call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if len(response.content) == 0:
                    raise ValueError("ACT - anthropic response is empty")
                outcome = response.content[0]
                if not isinstance(outcome, TextBlock):
                    raise ValueError("ACT - anthropic response is not text")
                response_str = AnthropicLLMClient.extract_json('{"' + outcome.text)
                self.logger.info(f"Received Actor response {response_str}")
                llm_response = LLMActResponse.model_validate(
                    ast.literal_eval(response_str or "")
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
        self.logger.debug(f"Assertor User Message:\n{conversation[-1].content}")
        expected_format = AnthropicLLMClient.generate_prompt_from_pydantic(
            LLMAssertResponse
        )
        conversation[-1].content += expected_format
        preshot_assistant = Message(
            role=MessageRole.Assistant,
            content='{"',
        )
        conversation.append(preshot_assistant)
        while attempts <= self.max_tries:
            try:
                response = await self.aclient.messages.create(
                    max_tokens=1000,
                    model="claude-3-5-sonnet-latest",
                    messages=self.to_anthropic_messages(conversation),
                    temperature=0,
                )

            except Exception as e:
                self.logger.error(f"Error #{attempts} in assert call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                attempts += 1
                continue
            try:
                if len(response.content) == 0:
                    raise ValueError("ASSERT - anthropic response is empty")
                outcome = response.content[0]
                if not isinstance(outcome, TextBlock):
                    raise ValueError("ASSERT - anthropic response is not text")
                response_str = AnthropicLLMClient.extract_json('{"' + outcome.text)
                self.logger.info(f"Received Assertor response {response_str}")
                llm_response = LLMAssertResponse.model_validate(
                    ast.literal_eval(response_str or "")
                )
                self.logger.info(
                    f"Received Assertor response {llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.error(f"Error #{attempts} in assert parsing: {str(e)}")
                if attempts >= self.max_tries:
                    raise
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
            expected_format = AnthropicLLMClient.generate_prompt_from_pydantic(
                LLMDataExtractionResponse
            )
            conversation[-1].content += expected_format
            preshot_assistant = Message(
                role=MessageRole.Assistant,
                content='{"',
            )
            conversation.append(preshot_assistant)
            try:
                response = await self.aclient.messages.create(
                    max_tokens=1024,
                    model="claude-3-5-sonnet-latest",
                    messages=self.to_anthropic_messages(conversation),
                    temperature=0,
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
                if len(response.content) == 0:
                    raise ValueError("Data Extraction - anthropic response is empty")
                outcome = response.content[0]
                if not isinstance(outcome, TextBlock):
                    raise ValueError("Data Extraction - anthropic response is not text")
                response_str = AnthropicLLMClient.extract_json('{"' + outcome.text)
                llm_response = LLMDataExtractionResponse.model_validate(
                    ast.literal_eval(response_str or "")
                )

                self.logger.info(
                    f"Received Data Extraction response:\n{llm_response.model_dump_json(indent=4)}"
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
    def to_anthropic_messages(conversation: list[Message]) -> Iterable[MessageParam]:
        messages: Iterable[MessageParam] = []
        for msg in conversation:
            match msg.role:
                case MessageRole.System:
                    continue
                case MessageRole.Assistant:
                    messages.append(MessageParam(role="assistant", content=msg.content))
                case MessageRole.User:
                    content: Iterable[TextBlockParam | ImageBlockParam] = []
                    content.append(TextBlockParam(type="text", text=msg.content))
                    if msg.screenshot:
                        for screenshot in msg.screenshot:
                            base64_screenshot = str(
                                base64.b64encode(screenshot), "utf-8"
                            )
                            image = Source(
                                media_type="image/png",
                                data=base64_screenshot,
                                type="base64",
                            )
                            content.append(ImageBlockParam(source=image, type="image"))
                    messages.append(MessageParam(content=content, role="user"))
        return messages

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
