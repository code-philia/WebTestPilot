import ast
import base64
import json
from logging import Logger
import os
import time
from typing import override
from uuid import uuid4

from mistralai import Mistral
from mistralai.models import (
    AssistantMessage,
    ImageURL,
    ImageURLChunk,
    Messages,
    SystemMessage,
    TextChunk,
    UserMessage,
    UserMessageContent,
)
from pydantic import BaseModel

from VTAAS.llm.llm_client import LLMClient


from ..schemas.llm import (
    Message,
    MessageRole,
    WorkerConfig,
    WorkerType,
    LLMActResponse,
    LLMAssertResponse,
    LLMDataExtractionResponse,
    LLMTestStepFollowUpResponse,
    LLMTestStepPlanResponse,
    LLMTestStepRecoverResponse,
    SequenceType,
)

from ..utils.logger import get_logger
from ..utils.config import load_config
import sys


class MistralLLMClient(LLMClient):
    """Communication with Mistral"""

    def __init__(
        self,
        name: str,
        start_time: float,
        output_folder: str,
        model: str = "pixtral-large-latest",
    ):
        load_config()
        self.start_time: float = start_time
        self.output_folder: str = output_folder
        self.model: str = model
        self.name: str = name
        self.logger: Logger = get_logger(
            "Mistral LLM Client - " + self.name + " - " + uuid4().hex,
            self.start_time,
            self.output_folder,
        )
        self.max_tries: int = 3
        try:
            self.aclient: Mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        except Exception as e:
            self.logger.fatal(e, exc_info=True)
            sys.exit(1)

    @override
    async def plan_step(self, conversation: list[Message]) -> LLMTestStepPlanResponse:
        """Get list of act/assert workers from LLM."""
        attempts = 1
        expected_format = MistralLLMClient.generate_prompt_from_pydantic_model(
            LLMTestStepPlanResponse(
                current_step_analysis="{{ current step analysis }}",
                screenshot_analysis="{{ screenshot analysis }}",
                previous_actions_analysis="{{ previous actions analysis }}",
                workers=[
                    WorkerConfig(type=WorkerType.ACTOR, query="act query"),
                    WorkerConfig(type=WorkerType.ASSERTOR, query="assert query"),
                ],
                sequence_type=SequenceType.full,
            )
        )
        conversation[-1].content += expected_format
        preshot_assistant = Message(
            role=MessageRole.Assistant,
            content='{"',
        )
        conversation.append(preshot_assistant)
        while attempts <= self.max_tries:
            try:
                self.logger.debug(
                    f"Init Plan Step Message:\n{conversation[-1].content}"
                )
                # resp_format = ResponseFormat(
                #     type="json_schema",
                #     json_schema=JSONSchema(
                #         name="Test step plan response",
                #         schema_definition=LLMTestStepPlanResponse.model_json_schema(),
                #     ),
                # )
                response = await self.aclient.chat.complete_async(
                    model=self.model,
                    messages=self._to_mistral_messages(conversation),
                    temperature=0,
                    frequency_penalty=0.7,
                    response_format={"type": "json_object"},
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
                self.logger.info(f"Raw response: {response.choices[0].message.content}")
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
                response = await self.aclient.chat.complete_async(
                    model=self.model,
                    messages=self._to_mistral_messages(conversation),
                    temperature=0,
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
                response = await self.aclient.chat.complete_async(
                    model=self.model,
                    messages=self._to_mistral_messages(conversation),
                    temperature=0,
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
                response = await self.aclient.chat.complete_async(
                    model=self.model,
                    messages=self._to_mistral_messages(conversation),
                    temperature=0,
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
                response = await self.aclient.chat.complete_async(
                    model=self.model,
                    messages=self._to_mistral_messages(conversation),
                    temperature=0,
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
                response = await self.aclient.chat.complete_async(
                    model=self.model,
                    messages=self._to_mistral_messages(conversation),
                    temperature=0,
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

    def _to_mistral_messages(self, conversation: list[Message]) -> list[Messages]:
        messages: list[Messages] = []
        for msg in conversation:
            match msg.role:
                case MessageRole.System:
                    messages.append(SystemMessage(role="system", content=msg.content))
                case MessageRole.Assistant:
                    messages.append(
                        AssistantMessage(role="assistant", content=msg.content)
                    )
                case MessageRole.User:
                    content: UserMessageContent = []
                    content.append(TextChunk(type="text", text=msg.content))
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
                                ImageURLChunk(image_url=image, type="image_url")
                            )
                    messages.append(UserMessage(content=content, role="user"))
        if isinstance(messages[-1], AssistantMessage):
            messages[-1].prefix = True
        return messages

    @staticmethod
    def generate_prompt_from_pydantic_model(model: BaseModel) -> str:
        """
        Mistral is supposed to handle structured outputs but does not. Let's ask the model to adhere to the format in the prompt
        """
        schema = model.model_dump_json(indent=2)
        prompt = (
            "\nYour response must be a json.loads parsable JSON object, similar to this:\n"
            f"{json.dumps(schema, indent=2)}"
            # "\n please omit properties that have a default null if you don't plan on valuing them"
        )
        return prompt

    @staticmethod
    def generate_prompt_from_pydantic(model: type[BaseModel]) -> str:
        """
        Mistral is supposed to handle structured outputs but does not. Let's ask the model to adhere to the format in the prompt
        """
        schema = model.model_json_schema()
        prompt = (
            "\nYour response must be a json.loads parsable JSON object, similar to this:\n"
            f"{json.dumps(schema, indent=2)}"
            # "\n please omit properties that have a default null if you don't plan on valuing them"
        )
        return prompt

    @staticmethod
    def extract_json(response: str) -> str:
        json_start = response.index("{")
        json_end = response.rfind("}")
        return response[json_start : json_end + 1]
