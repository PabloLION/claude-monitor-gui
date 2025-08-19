"""Usage examples for the Claude Monitor API wrapper.

This module demonstrates how to use the backward compatibility API wrapper
to analyze Claude usage data in various ways.
"""

import json
from typing import Any

# Import functions directly from the analysis module
from claude_monitor.data.analysis import analyze_usage
from claude_monitor.types import AnalysisResult, SerializedBlock
from claude_monitor.utils.formatting import format_currency, format_time


# Create helper functions that replace the removed facade functions
def analyze_usage_with_metadata(
    hours_back: int = 96, use_cache: bool = True, quick_start: bool = False, data_path: str | None = None
) -> AnalysisResult:
    """Enhanced analyze_usage with comprehensive metadata."""
    return analyze_usage(
        hours_back=hours_back,
        use_cache=use_cache,
        quick_start=quick_start,
        data_path=data_path,
    )


def analyze_usage_json(hours_back: int = 96, use_cache: bool = True, data_path: str | None = None, indent: int = 2) -> str:
    """Analyze usage and return JSON string."""
    result = analyze_usage(
        hours_back=hours_back, use_cache=use_cache, data_path=data_path
    )
    return json.dumps(result, indent=indent, default=str)


def get_usage_summary(hours_back: int = 96, use_cache: bool = True, data_path: str | None = None) -> dict[str, Any]:
    """Get high-level usage summary statistics."""
    result = analyze_usage(
        hours_back=hours_back, use_cache=use_cache, data_path=data_path
    )
    blocks = result.get("blocks", [])
    return _create_summary_stats(blocks)


def print_usage_json(hours_back: int = 96, use_cache: bool = True, data_path: str | None = None) -> None:
    """Print usage analysis as JSON to stdout."""
    json_result = analyze_usage_json(
        hours_back=hours_back, use_cache=use_cache, data_path=data_path
    )
    print(json_result)


def print_usage_summary(hours_back: int = 96, use_cache: bool = True, data_path: str | None = None) -> None:
    """Print human-readable usage summary."""
    summary = get_usage_summary(
        hours_back=hours_back, use_cache=use_cache, data_path=data_path
    )

    if summary.get("error"):
        print(f"Error: {summary.get('error_details', 'Unknown error')}")
        return

    print(f"Claude Usage Summary (Last {hours_back} Hours)")
    print("=" * 50)
    print(f"Total Sessions: {summary.get('total_sessions', 0)}")
    print(f"Total Cost: {format_currency(summary.get('total_cost', 0))}")
    print(f"Total Tokens: {summary.get('total_tokens', 0):,}")
    print(
        f"Average Session Cost: {format_currency(summary.get('average_session_cost', 0))}"
    )

    if summary.get("active_sessions", 0) > 0:
        print(f"Active Sessions: {summary['active_sessions']}")

    if summary.get("total_duration_minutes", 0) > 0:
        print(f"Total Duration: {format_time(summary['total_duration_minutes'])}")


def _create_summary_stats(blocks: list[SerializedBlock]) -> dict[str, Any]:
    """Create summary statistics from session blocks."""
    if not blocks:
        return {
            "total_sessions": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "average_session_cost": 0.0,
            "active_sessions": 0,
            "total_duration_minutes": 0,
        }

    total_sessions = len(blocks)
    total_cost = sum(block.get("cost", 0) for block in blocks)
    total_tokens = sum(block.get("tokens", {}).get("total", 0) for block in blocks)
    active_sessions = sum(1 for block in blocks if block.get("is_active", False))
    total_duration_minutes = sum(block.get("duration_minutes", 0) for block in blocks)

    average_session_cost = total_cost / total_sessions if total_sessions > 0 else 0

    return {
        "total_sessions": total_sessions,
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "average_session_cost": average_session_cost,
        "active_sessions": active_sessions,
        "total_duration_minutes": total_duration_minutes,
    }


# For backward compatibility
analyze_usage_direct = analyze_usage


def example_basic_usage() -> None:
    """Example 1: Basic usage (backward compatibility with original API)

    This example shows how to use the API in the same way as the original
    usage_analyzer.api.analyze_usage() function.
    """
    print("=== Example 1: Basic Usage ===")

    try:
        # Simple usage - returns analysis result
        result = analyze_usage()
        blocks = result.get("blocks", [])

        print(f"Found {len(blocks)} session blocks")

        # Process blocks just like the original API
        for block in blocks:
            # Access block data safely with type ignores for dynamic serialized data
            block_id = block.get("id", "unknown")  # type: ignore[typeddict-item]
            total_tokens = block.get("totalTokens", 0)  # type: ignore[typeddict-item]
            cost_usd = block.get("costUSD", 0.0)  # type: ignore[typeddict-item]
            print(
                f"Block {block_id}: {total_tokens} tokens, ${cost_usd:.2f}"
            )

            is_active = block.get("isActive", False)  # type: ignore[typeddict-item]
            if is_active:
                duration_minutes = block.get("durationMinutes", 0.0)  # type: ignore[typeddict-item]
                print(f"  - Active block with {duration_minutes:.1f} minutes")

                # Check for burn rate data
                if "burnRate" in block:
                    burn_rate = block.get("burnRate", {})  # type: ignore[typeddict-item]
                    # Type ignore for serialized data access
                    if burn_rate:  # type: ignore[truthy-bool]
                        tokens_per_min = burn_rate.get("tokensPerMinute", 0.0)
                        print(
                            f"  - Burn rate: {tokens_per_min:.1f} tokens/min"
                        )

                # Check for projections
                if "projection" in block:
                    proj = block.get("projection", {})  # type: ignore[typeddict-item]
                    # Type ignore for serialized data access
                    if proj:  # type: ignore[truthy-bool]
                        proj_tokens = proj.get("totalTokens", 0)
                        proj_cost = proj.get("totalCost", 0.0)
                        print(
                            f"  - Projected: {proj_tokens} tokens, ${proj_cost:.2f}"
                        )

    except Exception as e:
        print(f"Error: {e}")


def example_advanced_usage() -> None:
    """Example 2: Advanced usage with metadata and time filtering

    This example shows how to use the enhanced features of the new API
    while maintaining backward compatibility.
    """
    print("\n=== Example 2: Advanced Usage ===")

    try:
        # Get full results with metadata
        result = analyze_usage_with_metadata(
            hours_back=24,  # Only last 24 hours
            quick_start=True,  # Fast analysis
        )

        blocks = result.get("blocks", [])
        metadata = result.get("metadata", {})

        # Type ignore for metadata access
        load_time = metadata.get("load_time_seconds", 0.0)  # type: ignore[misc]
        entries_processed = metadata.get("entries_processed", 0)  # type: ignore[misc]
        blocks_created = metadata.get("blocks_created", 0)  # type: ignore[misc]
        print(f"Analysis completed in {load_time:.3f}s")  # type: ignore[str-format]
        print(f"Processed {entries_processed} entries")  # type: ignore[str-format]
        print(f"Created {blocks_created} blocks")  # type: ignore[str-format]

        # Find active blocks
        active_blocks = [b for b in blocks if b.get("isActive", False)]  # type: ignore[typeddict-item]
        print(f"Active blocks: {len(active_blocks)}")

        # Calculate total usage
        total_cost = sum(b.get("costUSD", 0.0) for b in blocks)  # type: ignore[typeddict-item]
        total_tokens = sum(b.get("totalTokens", 0) for b in blocks)  # type: ignore[typeddict-item]

        print(f"Total usage: {total_tokens:,} tokens, ${total_cost:.2f}")

    except Exception as e:
        print(f"Error: {e}")


def example_json_output() -> None:
    """Example 3: JSON output (same as original API when used as script)

    This example shows how to get JSON output exactly like the original API.
    """
    print("\n=== Example 3: JSON Output ===")

    try:
        # Get JSON string (same format as original)
        json_output = analyze_usage_json(hours_back=48)

        # Parse it back to verify
        parsed_data = json.loads(json_output)
        if isinstance(parsed_data, dict) and "blocks" in parsed_data:
            blocks = parsed_data["blocks"]  # type: ignore[assignment]
        elif isinstance(parsed_data, list):
            blocks = parsed_data  # type: ignore[assignment]
        else:
            blocks = []
        print(f"JSON contains {len(blocks)} blocks")  # type: ignore[arg-type]

        # Print a formatted sample
        if blocks:
            sample_block = blocks[0]  # type: ignore[index]
            print("\nSample block structure:")
            print(json.dumps(sample_block, indent=2)[:500] + "...")  # type: ignore[arg-type]

    except Exception as e:
        print(f"Error: {e}")


def example_usage_summary() -> None:
    """Example 4: Usage summary and statistics

    This example shows how to get high-level statistics about usage.
    """
    print("\n=== Example 4: Usage Summary ===")

    try:
        # Get summary statistics
        summary = get_usage_summary(hours_back=168)  # Last week

        print(f"Total Cost: ${summary.get('total_cost', 0.0):.2f}")
        print(f"Total Tokens: {summary.get('total_tokens', 0):,}")
        print(f"Total Blocks: {summary.get('total_sessions', 0)}")
        print(f"Active Blocks: {summary.get('active_sessions', 0)}")

        # Model breakdown
        print("\nModel usage:")
        model_stats = summary.get("model_stats", {})
        if model_stats:
            for model, stats in model_stats.items():  # type: ignore[misc]
                if stats:
                    tokens = stats.get('tokens', 0)  # type: ignore[misc]
                    cost = stats.get('cost', 0.0)  # type: ignore[misc]
                    print(f"  {model}: {tokens:,} tokens, ${cost:.2f}")  # type: ignore[str-format]

        # Performance info
        perf = summary.get("performance", {})
        if perf:
            load_time = perf.get('load_time_seconds', 0.0)  # type: ignore[misc]
            print(f"\nPerformance: {load_time:.3f}s load time")  # type: ignore[str-format]

    except Exception as e:
        print(f"Error: {e}")


def example_custom_data_path() -> None:
    """Example 5: Using custom data path

    This example shows how to analyze data from a custom location.
    """
    print("\n=== Example 5: Custom Data Path ===")

    try:
        # You can specify a custom path to Claude data
        custom_path = "/path/to/claude/data"  # Replace with actual path

        # This will use the custom path instead of default ~/.claude/projects
        result = analyze_usage(
            data_path=custom_path,
            hours_back=24,
            quick_start=True,
        )
        blocks = result.get("blocks", [])

        print(f"Analyzed {len(blocks)} blocks from custom path")

    except Exception as e:
        print(f"Error (expected if path doesn't exist): {e}")


def example_direct_import() -> None:
    """Example 6: Direct import from main module

    This example shows how to import the function directly from the main module.
    """
    print("\n=== Example 6: Direct Import ===")

    try:
        # You can import directly from claude_monitor module
        result = analyze_usage_direct()
        blocks = result.get("blocks", [])

        print(f"Direct import worked! Found {len(blocks)} blocks")

    except Exception as e:
        print(f"Error: {e}")


def example_error_handling() -> None:
    """Example 7: Error handling patterns

    This example shows how the API handles errors gracefully.
    """
    print("\n=== Example 7: Error Handling ===")

    try:
        # This might fail if no data is available
        result = analyze_usage(
            data_path="/nonexistent/path",
            hours_back=1,
        )
        blocks = result.get("blocks", [])

        print(f"Success: {len(blocks)} blocks")

    except Exception as e:
        print(f"Handled error gracefully: {e}")
        print("The API reports errors to logging")


def example_print_functions() -> None:
    """Example 8: Print functions for direct output

    This example shows the convenience print functions.
    """
    print("\n=== Example 8: Print Functions ===")

    try:
        # Print JSON directly (like original API as script)
        print("JSON output:")
        print_usage_json(hours_back=24)

        print("\nSummary output:")
        print_usage_summary(hours_back=24)

    except Exception as e:
        print(f"Error: {e}")


def example_compatibility_check() -> None:
    """Example 9: Compatibility check with original API

    This example shows how to verify the output is compatible with the original.
    """
    print("\n=== Example 9: Compatibility Check ===")

    try:
        # Get data in original format
        result = analyze_usage()
        blocks = result.get("blocks", [])

        # Check structure matches original expectations
        if blocks:
            block = blocks[0]
            required_fields = [
                "id",
                "isActive",
                "isGap",
                "startTime",
                "endTime",
                "totalTokens",
                "costUSD",
                "models",
                "durationMinutes",
            ]

            missing_fields = [field for field in required_fields if field not in block]  # type: ignore[operator]

            if missing_fields:
                print(f"Missing fields: {missing_fields}")
            else:
                print("All required fields present - compatible with original API")

            # Check for enhanced fields
            enhanced_fields = ["burnRate", "projection", "limitMessages"]
            present_enhanced = [field for field in enhanced_fields if field in block]  # type: ignore[operator]

            if present_enhanced:
                print(f"Enhanced fields available: {present_enhanced}")

    except Exception as e:
        print(f"Error: {e}")


def run_all_examples() -> None:
    """Run all examples to demonstrate the API functionality."""
    print("Claude Monitor API Examples")
    print("=" * 50)

    examples = [
        example_basic_usage,
        example_advanced_usage,
        example_json_output,
        example_usage_summary,
        example_custom_data_path,
        example_direct_import,
        example_error_handling,
        example_print_functions,
        example_compatibility_check,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")

    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    run_all_examples()
