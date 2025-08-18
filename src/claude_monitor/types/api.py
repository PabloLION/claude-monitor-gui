"""Claude API message types and related structures."""

from typing import Literal, NotRequired, Required, TypedDict


class MessageContentBase(TypedDict, total=False):
    """Base structure for all message content types."""

    id: NotRequired[str]
    role: NotRequired[str]


class SystemMessageContent(MessageContentBase, total=False):
    """Structure for system message content."""

    content: NotRequired[str]
    text: NotRequired[str]


class UserMessageContent(MessageContentBase, total=False):
    """Structure for user message content."""

    content: NotRequired[str | list[dict[str, str]]]
    text: NotRequired[str]
    attachments: NotRequired[list[dict[str, str]]]


class AssistantMessageContent(MessageContentBase, total=False):
    """Structure for assistant message content."""

    model: NotRequired[str]
    usage: NotRequired["TokenUsage"]
    content: NotRequired[str | list[dict[str, str]]]


class ClaudeEntryBase(TypedDict, total=False):
    """Base class for all Claude API message entries."""

    timestamp: Required[str]
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name


class SystemEntry(ClaudeEntryBase, total=False):
    """System messages from Claude (type='system')."""

    type: Required[Literal["system"]]
    content: NotRequired[str]  # For backward compatibility
    message: NotRequired[SystemMessageContent]


class UserEntry(ClaudeEntryBase, total=False):
    """User messages (type='user')."""

    type: Required[Literal["user"]]
    message: Required[UserMessageContent]


class AssistantEntry(ClaudeEntryBase, total=False):
    """Assistant responses with token usage (type='assistant')."""

    type: Required[Literal["assistant"]]
    model: NotRequired[str]  # Model might not always be present
    message: NotRequired[AssistantMessageContent]
    usage: NotRequired[dict[str, int]]
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    cost: NotRequired[float]
    cost_usd: NotRequired[float]


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
