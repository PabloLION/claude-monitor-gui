import time
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from statistics import quantiles
from collections.abc import Callable

from claude_monitor.core.models import JSONSerializable


@dataclass(frozen=True)
class P90Config:
    common_limits: Sequence[int]
    limit_threshold: float
    default_min_limit: int
    cache_ttl_seconds: int


def _did_hit_limit(tokens: int, common_limits: Sequence[int], threshold: float) -> bool:
    return any(tokens >= limit * threshold for limit in common_limits)


def _extract_sessions(
    blocks: Sequence[dict[str, JSONSerializable]], filter_fn: Callable[[dict[str, JSONSerializable]], bool]
) -> list[int]:
    tokens: list[int] = []
    for block in blocks:
        if filter_fn(block):
            total_tokens_raw = block.get("totalTokens", 0)
            if isinstance(total_tokens_raw, (int, float)) and total_tokens_raw > 0:
                tokens.append(int(total_tokens_raw))
    return tokens


def _calculate_p90_from_blocks(blocks: Sequence[dict[str, JSONSerializable]], cfg: P90Config) -> int:
    def hit_limit_filter(b: dict[str, JSONSerializable]) -> bool:
        if b.get("isGap", False) or b.get("isActive", False):
            return False
        total_tokens_raw = b.get("totalTokens", 0)
        if isinstance(total_tokens_raw, (int, float)):
            return _did_hit_limit(int(total_tokens_raw), cfg.common_limits, cfg.limit_threshold)
        return False
    
    hits = _extract_sessions(blocks, hit_limit_filter)
    if not hits:
        hits = _extract_sessions(
            blocks, lambda b: not b.get("isGap", False) and not b.get("isActive", False)
        )
    if not hits:
        return cfg.default_min_limit
    q: float = quantiles(hits, n=10)[8]
    return max(int(q), cfg.default_min_limit)


class P90Calculator:
    def __init__(self, config: P90Config | None = None) -> None:
        if config is None:
            from claude_monitor.core.plans import (
                COMMON_TOKEN_LIMITS,
                DEFAULT_TOKEN_LIMIT,
                LIMIT_DETECTION_THRESHOLD,
            )

            config = P90Config(
                common_limits=COMMON_TOKEN_LIMITS,
                limit_threshold=LIMIT_DETECTION_THRESHOLD,
                default_min_limit=DEFAULT_TOKEN_LIMIT,
                cache_ttl_seconds=60 * 60,
            )
        self._cfg: P90Config = config

    @lru_cache(maxsize=1)
    def _cached_calc(
        self, key: int, blocks_tuple: tuple[tuple[bool, bool, int], ...]
    ) -> int:
        blocks: list[dict[str, JSONSerializable]] = [
            {"isGap": g, "isActive": a, "totalTokens": t} for g, a, t in blocks_tuple
        ]
        return _calculate_p90_from_blocks(blocks, self._cfg)

    def calculate_p90_limit(
        self,
        blocks: list[dict[str, JSONSerializable]] | None = None,
        use_cache: bool = True,
    ) -> int | None:
        if not blocks:
            return None
        if not use_cache:
            return _calculate_p90_from_blocks(blocks, self._cfg)
        ttl: int = self._cfg.cache_ttl_seconds
        expire_key: int = int(time.time() // ttl)
        blocks_tuple: tuple[tuple[bool, bool, int], ...] = tuple(
            (
                bool(b.get("isGap", False)),
                bool(b.get("isActive", False)),
                (
                    int(total_tokens) 
                    if isinstance((total_tokens := b.get("totalTokens", 0)), (int, float)) 
                    else 0
                ),
            )
            for b in blocks
        )
        return self._cached_calc(expire_key, blocks_tuple)
