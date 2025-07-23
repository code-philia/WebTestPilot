import ast
from copy import deepcopy
import json
import time
from typing import final, override
from uuid import uuid4
from google import genai
from google.genai import types
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


@final
class GoogleLLMClient(LLMClient):
    """Communication with OpenAI"""

    def __init__(self, name: str, start_time: float, output_folder: str):
        load_config()
        self.start_time = start_time
        self.output_folder = output_folder
        self.max_tries = 3
        self.name: str = name
        self.logger = get_logger(
            "Google LLM Client - " + self.name + " - " + uuid4().hex,
            self.start_time,
            self.output_folder,
        )
        self.client = genai.Client()

    @override
    async def plan_step(self, conversation: list[Message]) -> LLMTestStepPlanResponse:
        """Get list of act/assert workers from LLM."""
        attempts = 1
        while attempts <= self.max_tries:
            try:
                self.logger.debug(
                    f"Init Plan Step Message:\n{conversation[-1].content}"
                )
                response = self.client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=self._to_google_messages(conversation),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LLMTestStepPlanResponse,
                        temperature=0,
                        seed=192837465,
                    ),
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan step call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                time.sleep(20)
                attempts += 1
                continue

            try:
                llm_response = LLMTestStepPlanResponse.model_validate(
                    ast.literal_eval(response.text or "")
                )
                self.logger.info(
                    f"Orchestrator Plan response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.info(f"Raw response:\n{response.text}")
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
                response = self.client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=self._to_google_messages(conversation),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LLMTestStepFollowUpResponse,
                        temperature=0,
                        seed=192837465,
                    ),
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan followup call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                time.sleep(20)
                attempts += 1
                continue
            try:
                llm_response = LLMTestStepFollowUpResponse.model_validate(
                    ast.literal_eval(response.text or "")
                )
                self.logger.info(
                    f"Orchestrator Follow-Up response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.info(f"Raw response:\n{response.text}")
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
                response = self.client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=self._to_google_messages(conversation),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LLMTestStepRecoverResponse,
                        temperature=0,
                        seed=192837465,
                    ),
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in plan recover call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                time.sleep(20)
                attempts += 1
                continue
            try:
                llm_response = LLMTestStepRecoverResponse.model_validate(
                    ast.literal_eval(response.text or "")
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
                self.logger.info(f"Raw response:\n{response.text}")
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
        error_suffix = ""
        expected_format = GoogleLLMClient.generate_prompt_from_pydantic(LLMActResponse)
        conversation[-1].content += expected_format
        while attempts <= self.max_tries:
            convo = deepcopy(conversation)
            convo[-1].content += error_suffix
            if error_suffix:
                self.logger.info(
                    f"user message after error_suffix:\n{convo[-1].content}"
                )
            try:
                # self.logger.debug(f"Actor User Message:\n{conversation[-1].content}")
                response = self.client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=self._to_google_messages(convo),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        # response_schema=LLMActGoogleResponse,
                        temperature=0
                        + (
                            0.2 * (attempts - 1)
                        ),  # We increase the temp with the failures to expect a different output
                        seed=192837465,
                    ),
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in act call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                time.sleep(20)
                attempts += 1
                continue
            try:
                if not response.text:
                    raise Exception("LLM response is empty")
                self.logger.debug(f"Received Actor raw response:\n{response.text}")
                llm_response = LLMActResponse.model_validate(
                    ast.literal_eval(response.text or "")
                )
                self.logger.info(
                    f"Actor response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.info(f"Raw response:\n{response.text}")
                self.logger.error(f"Error #{attempts} in act parsing: {str(e)}")
                error_suffix = (
                    "\nNote that your last answer could not be parsed by pydantic:"
                    f"\n{str(e)}\nPlease ensure you respect the provided response schema. "
                    "In case of a failed status, make sure to explicitely mention the finish command."
                )
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
                response = self.client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=self._to_google_messages(conversation),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LLMAssertResponse,
                        temperature=0,
                        seed=192837465,
                    ),
                )
            except Exception as e:
                self.logger.error(f"Error #{attempts} in assert call: {str(e)}")
                if attempts >= self.max_tries:
                    raise
                time.sleep(20)
                attempts += 1
                continue
            try:
                if not response.text:
                    raise Exception("LLM response is empty")
                llm_response = LLMAssertResponse.model_validate(
                    ast.literal_eval(response.text or "")
                )
                self.logger.info(
                    f"Received Assertor response {llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.info(f"Raw response:\n{response.text}")
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
                response = self.client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=self._to_google_messages(conversation),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LLMDataExtractionResponse,
                        temperature=0,
                        seed=192837465,
                    ),
                )
            except Exception as e:
                self.logger.error(
                    f"Error #{attempts} in data extraction call: {str(e)}"
                )
                if attempts >= self.max_tries:
                    raise
                time.sleep(20)
                attempts += 1
                continue
            try:
                resp_msg = response.text
                if not resp_msg:
                    raise Exception("Data extraction response is empty")
                llm_response = LLMDataExtractionResponse.model_validate(
                    ast.literal_eval(response.text or "")
                )

                self.logger.info(
                    f"Received Data Extraction response:\n{llm_response.model_dump_json(indent=4)}"
                )
                return llm_response

            except Exception as e:
                self.logger.info(f"Raw response:\n{response.text}")
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
        Google has trouble adhering to certain schemas, especially for the act call
        """
        schema = model.model_json_schema()
        prompt = (
            "\nYour response must be a json.loads parsable JSON object, following this Pydantic JSON schema:\n"
            f"{json.dumps(schema, indent=2)}"
            "\n please omit properties that have a default null if you don't plan on valuing them"
        )
        return prompt

    def _to_google_messages(
        self, conversation: list[Message]
    ) -> list[types.ContentUnion]:
        messages: list[types.ContentUnion] = []
        for msg in conversation:
            match msg.role:
                case MessageRole.Assistant:
                    messages.append(
                        types.Content(
                            role="model", parts=[types.Part(text=msg.content)]
                        )
                    )
                case MessageRole.User:
                    content: list[types.Part] = [types.Part(text=msg.content)]
                    if msg.screenshot:
                        for screenshot in msg.screenshot:
                            content.append(
                                types.Part.from_bytes(
                                    data=screenshot,
                                    mime_type="image/png",
                                )
                            )
                    messages.append(types.Content(role="user", parts=content))
                case _:  # we dismiss system prompts with google, for now
                    continue
        return messages
