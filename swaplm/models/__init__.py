"""Pydantic request and response schemas.

Re-exports every public model so consumers can write::

    from swaplm.models import ChatRequest, ChatResponse, Message
"""

from swaplm.models.messages import (
    FunctionCall,
    FunctionCallDelta,
    FunctionDefinition,
    ImageContent,
    ImageURL,
    Message,
    TextContent,
    Tool,
    ToolCall,
    ToolCallDelta,
)
from swaplm.models.model import ModelInfo
from swaplm.models.provider import ProviderInfo
from swaplm.models.request import ChatRequest
from swaplm.models.response import ChatResponse, Choice, Usage
from swaplm.models.stream import ChoiceDelta, ChunkChoice, StreamChunk

__all__ = [
    # Request
    "ChatRequest",
    # Response
    "ChatResponse",
    "Choice",
    "ChoiceDelta",
    # Stream
    "ChunkChoice",
    # Messages
    "FunctionCall",
    "FunctionCallDelta",
    "FunctionDefinition",
    "ImageContent",
    "ImageURL",
    "Message",
    # Provider / Model metadata
    "ModelInfo",
    "ProviderInfo",
    "StreamChunk",
    "TextContent",
    "Tool",
    "ToolCall",
    "ToolCallDelta",
    "Usage",
]
