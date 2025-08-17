"""Claude API message types and related structures."""

from typing import Literal, NotRequired, TypedDict


class SystemEntry(TypedDict, total=False):
    """System messages from Claude (type='system')."""

    type: Literal["system"]
    timestamp: str
    content: str
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name


class UserEntry(TypedDict, total=False):
    """User messages (type='user')."""

    type: Literal["user"]
    timestamp: str
    message: dict[str, str | int | list[dict[str, str]] | dict[str, str]]
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name


class AssistantEntry(TypedDict, total=False):
    """Assistant responses with token usage (type='assistant')."""

    type: Literal["assistant"]
    timestamp: str
    model: str
    message: dict[str, "str | int | TokenUsage"]
    usage: dict[str, int]
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    cost: NotRequired[float]
    cost_usd: NotRequired[float]
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name


# Discriminated union for all Claude JSONL entry types
ClaudeJSONEntry = SystemEntry | UserEntry | AssistantEntry


class TokenUsage(TypedDict, total=False):
    """Token usage information from various sources."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cache_creation_input_tokens: int  # Alternative field name
    cache_read_input_tokens: int  # Alternative field name
    inputTokens: int  # Alternative field name (camelCase)
    outputTokens: int  # Alternative field name (camelCase)
    cacheCreationInputTokens: int  # Alternative field name (camelCase)
    cacheReadInputTokens: int  # Alternative field name (camelCase)
    prompt_tokens: int  # Alternative field name (OpenAI format)
    completion_tokens: int  # Alternative field name (OpenAI format)
    total_tokens: int