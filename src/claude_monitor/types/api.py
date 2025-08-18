"""Claude API message types and related structures."""

from typing import Literal
from typing import NotRequired
from typing import Required
from typing import TypedDict


class BaseMessageContent(TypedDict, total=False):
    """Base structure for all message content types."""

    id: NotRequired[str]
    role: NotRequired[str]


class SystemMessage(BaseMessageContent, total=False):
    """Structure for system message content."""

    content: NotRequired[str]
    text: NotRequired[str]


class UserMessage(BaseMessageContent, total=False):
    """Structure for user message content."""

    content: NotRequired[str | list[dict[str, str]]]
    text: NotRequired[str]
    attachments: NotRequired[list[dict[str, str]]]


class AssistantMessage(BaseMessageContent, total=False):
    """Structure for assistant message content."""

    model: NotRequired[str]
    usage: NotRequired["TokenUsageData"]
    content: NotRequired[str | list[dict[str, str]]]


class BaseClaudeEntry(TypedDict, total=False):
    """Base class for all Claude API message entries."""

    timestamp: Required[str]
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name


class SystemMessageEntry(BaseClaudeEntry, total=False):
    """System messages from Claude (type='system')."""

    type: Required[Literal["system"]]
    content: NotRequired[str]  # For backward compatibility
    message: NotRequired[SystemMessage]


class UserMessageEntry(BaseClaudeEntry, total=False):
    """User messages (type='user')."""

    type: Required[Literal["user"]]
    message: Required[UserMessage]


class AssistantMessageEntry(BaseClaudeEntry, total=False):
    """Assistant responses with token usage (type='assistant')."""

    type: Required[Literal["assistant"]]
    model: NotRequired[str]  # Model might not always be present
    message: NotRequired[AssistantMessage]
    usage: NotRequired[dict[str, int]]
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    cost: NotRequired[float]
    cost_usd: NotRequired[float]


# Discriminated union for all Claude JSONL entry types
ClaudeMessageEntry = (
    SystemMessageEntry | UserMessageEntry | AssistantMessageEntry
)


class TokenUsageData(TypedDict, total=False):
    """Token usage information from various sources."""

    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    cache_creation_input_tokens: NotRequired[int]  # Alternative field name
    cache_read_input_tokens: NotRequired[int]  # Alternative field name
    inputTokens: NotRequired[int]  # Alternative field name (camelCase)
    outputTokens: NotRequired[int]  # Alternative field name (camelCase)
    cacheCreationInputTokens: NotRequired[
        int
    ]  # Alternative field name (camelCase)
    cacheReadInputTokens: NotRequired[int]  # Alternative field name (camelCase)
    prompt_tokens: NotRequired[int]  # Alternative field name (OpenAI format)
    completion_tokens: NotRequired[
        int
    ]  # Alternative field name (OpenAI format)
    total_tokens: NotRequired[int]
