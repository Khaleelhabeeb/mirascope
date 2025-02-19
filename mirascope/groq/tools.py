"""Classes for using tools with Groq's Cloud API."""

from __future__ import annotations

import json
from typing import Any, Callable, Type

from groq.types.chat.chat_completion import ChoiceMessageToolCall
from pydantic import BaseModel

from ..base import BaseTool, BaseType
from ..base.utils import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)


class GroqTool(BaseTool[ChoiceMessageToolCall]):
    '''A base class for easy use of tools with the Groq client.

    `GroqTool` internally handles the logic that allows you to use tools with simple
    calls such as `GroqCallResponse.tool` or `GroqTool.fn`, as seen in the  examples
    below.
    
    Example:

    ```python
    import os

    from mirascope.groq import GroqCall, GroqCallParams

    os.environ["GROQ_API_KEY"] = "YOUR_API_KEY"


    def animal_matcher(fav_food: str, fav_color: str) -> str:
        """Tells you your most likely favorite animal from personality traits.

        Args:
            fav_food: your favorite food.
            fav_color: your favorite color.

        Returns:
            The animal most likely to be your favorite based on traits.
        """
        return "Your favorite animal is the best one, a frog."


    class AnimalMatcher(GroqCall):
        prompt_template = """\\
            Tell me my favorite animal if my favorite food is {food} and my
            favorite color is {color}.
        """

        food: str
        color: str

        call_params = GroqCallParams(
            model="mixtral-8x7b-32768", tools=[animal_matcher]
        )


    prompt = AnimalMatcher(food="pizza", color="green")
    response = prompt.call()

    if tools := response.tools:
        for tool in tools:
            print(tool.fn(**tool.args))
    #> Your favorite animal is the best one, a frog.
    '''

    @classmethod
    def tool_schema(cls) -> dict[str, Any]:
        """Constructs a tool schema for use with the Groq Cloud API.

        A Mirascope `GroqTool` is deconstructed into a JSON schema, and relevant keys
        are renamed to match the schema used to make functional/tool calls in the Groq
        Cloud API.

        Returns:
            The constructed tool schema.
        """
        fn = super().tool_schema()
        return {"type": "function", "function": fn}

    @classmethod
    def from_tool_call(cls, tool_call: ChoiceMessageToolCall) -> GroqTool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given `ToolCall` from a Groq chat completion response, takes its function
        arguments and creates a `GroqTool` instance from it.

        Args:
            tool_call: The Groq `ToolCall` to extract the tool from.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValueError: if the tool call doesn't match the tool schema.
        """
        try:
            model_json = {}
            if tool_call.function and tool_call.function.arguments:
                model_json = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise ValueError() from e

        model_json["tool_call"] = tool_call
        return cls.model_validate(model_json)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[GroqTool]:
        """Constructs a `GroqTool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, GroqTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[GroqTool]:
        """Constructs a `GroqTool` type from a function."""
        return convert_function_to_tool(fn, GroqTool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseType]) -> Type[GroqTool]:
        """Constructs a `GroqTool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, GroqTool)
