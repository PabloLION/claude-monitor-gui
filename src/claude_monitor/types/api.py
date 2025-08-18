"""Claude API message types and related structures."""

from typing import Literal, NotRequired, Required, TypedDict


class SystemEntry(TypedDict, total=False):
    """System messages from Claude (type='system')."""

    type: Required[Literal["system"]]
    timestamp: Required[str]
    content: Required[str]
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name


class UserEntry(TypedDict, total=False):
    """User messages (type='user')."""

    type: Required[Literal["user"]]
    timestamp: Required[str]
    message: Required[dict[str, str | int | list[dict[str, str]] | dict[str, str]]]
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name


class AssistantEntry(TypedDict, total=False):
    """Assistant responses with token usage (type='assistant')."""

    type: Required[Literal["assistant"]]
    timestamp: Required[str]
    model: NotRequired[str]  # Model might not always be present
    message: NotRequired[dict[str, "str | int | TokenUsage"]]
    usage: NotRequired[dict[str, int]]
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

    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    cache_creation_input_tokens: NotRequired[int]  # Alternative field name
    cache_read_input_tokens: NotRequired[int]  # Alternative field name
    inputTokens: NotRequired[int]  # Alternative field name (camelCase)
    outputTokens: NotRequired[int]  # Alternative field name (camelCase)
    cacheCreationInputTokens: NotRequired[int]  # Alternative field name (camelCase)
    cacheReadInputTokens: NotRequired[int]  # Alternative field name (camelCase)
    prompt_tokens: NotRequired[int]  # Alternative field name (OpenAI format)
    completion_tokens: NotRequired[int]  # Alternative field name (OpenAI format)
    total_tokens: NotRequired[int]
