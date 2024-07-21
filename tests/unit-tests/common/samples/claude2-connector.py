import logging

import anthropic
from anthropic import AI_PROMPT, HUMAN_PROMPT
from anthropic.types import Completion

from moonshot.src.connectors.connector import Connector, perform_retry
from moonshot.src.connectors_endpoints.connector_endpoint_arguments import (
    ConnectorEndpointArguments,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Claude2Connector(Connector):
    def __init__(self, ep_arguments: ConnectorEndpointArguments):
        # Initialize super class
        super().__init__(ep_arguments)

        # Set Claude2 Key
        self._client = anthropic.AsyncAnthropic(api_key=self.token)

        # Set the model to use and remove it from optional_params if it exists
        self.model = self.optional_params.get("model", "")

    @Connector.rate_limited
    @perform_retry
    async def get_response(self, prompt: str) -> str:
        """
        Asynchronously sends a prompt to the Claude2 API and returns the generated response.

        This method constructs a request with the given prompt, optionally prepended and appended with
        predefined strings, and sends it to the Claude2 API. If a system prompt is set, it is included in the
        request. The method then awaits the response from the API, processes it, and returns the resulting message
        content as a string.

        Args:
            prompt (str): The input prompt to send to the Claude2 API.

        Returns:
            str: The text response generated by the Claude2 model.
        """
        connector_prompt = f"{self.pre_prompt}{prompt}{self.post_prompt}"
        # Merge self.optional_params with additional parameters
        new_params = {
            **self.optional_params,
            "model": self.model,
            "prompt": f"{HUMAN_PROMPT}{connector_prompt}{AI_PROMPT}",
        }
        response = await self._client.completions.create(**new_params)
        return await self._process_response(response)

    async def _process_response(self, response: Completion) -> str:
        """
        Process an HTTP response and extract relevant information as a string.

        This function takes an HTTP response object as input and processes it to extract
        relevant information as a string. The extracted information may include data
        from the response body, headers, or other attributes.

        Args:
            response (Completion): An HTTP response object containing the response data.

        Returns:
            str: A string representing the relevant information extracted from the response.
        """
        return response.completion[1:]
