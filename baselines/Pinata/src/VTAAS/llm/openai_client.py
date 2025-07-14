import ast
import base64
from collections.abc import Iterable
from logging import Logger
import time
from typing import override
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

from VTAAS.llm.llm_client import LLMClient


from ..schemas.llm import (
    LLMActResponse,
    LLMAssertResponse,
    LLMDataExtractionResponse,
    LLMTestStepFollowUpResponse,
    LLMTestStepPlanResponse,
    LLMTestStepRecoverResponse,
    Message,
    MessageRole,
)

from ..utils.logger import get_logger
from ..utils.config import load_config
import sys


class OpenAILLMClient(LLMClient):
    """Communication with OpenAI"""

    def __init__(
        self,
        name: str,
        start_time: float,
        output_folder: str,
        model: str = "gpt-4o-2024-11-20",
    ):
        load_config()
        self.start_time: float = start_time
        self.output_folder: str = output_folder
        self.model: str = model
        self.name: str = name
        self.logger: Logger = get_logger(
            "OpenAI LLM Client - " + self.name + " - " + uuid4().hex,
            self.start_time,
            self.output_folder,
        )
        self.max_tries: int = 3
        try:
            self.aclient: AsyncOpenAI = AsyncOpenAI()
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
        while attempts <= self.max_tries:
            try:
                self.logger.debug(f"Assertor User Message:\n{conversation[-1].content}")
                response = await self.aclient.beta.chat.completions.parse(
                    model=self.model,
                    messages=self._to_openai_messages(conversation),
                    temperature=0,
                    seed=192837465,
                    frequency_penalty=0.7,
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
