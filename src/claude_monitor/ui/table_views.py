"""Table views for daily and monthly statistics display.

This module provides UI components for displaying aggregated usage data
in table format using Rich library.
"""

import logging

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from claude_monitor.types import AggregatedTotals
from claude_monitor.types import JSONSerializable
from claude_monitor.types import TotalAggregatedData

# Removed theme import - using direct styles
from claude_monitor.utils.formatting import format_currency
from claude_monitor.utils.formatting import format_number


logger = logging.getLogger(__name__)


class TableViewsController:
    """Controller for table-based views (daily, monthly)."""

    def __init__(self, console: Console | None = None):
        """Initialize the table views controller.

        Args:
            console: Optional Console instance for rich output
        """
        self.console = console
        # Define simple styles
        self.key_style = "cyan"
        self.value_style = "white"
        self.accent_style = "yellow"
        self.success_style = "green"
        self.warning_style = "yellow"
        self.header_style = "bold cyan"
        self.table_header_style = "bold"
        self.border_style = "bright_blue"

    def _create_base_table(
        self, title: str, period_column_name: str, period_column_width: int
    ) -> Table:
        """Create a base table with common structure.

        Args:
            title: Table title
            period_column_name: Name for the period column ('Date' or 'Month')
            period_column_width: Width for the period column

        Returns:
            Rich Table object with columns added
        """
        table = Table(
            title=title,
            title_style="bold cyan",
            show_header=True,
            header_style="bold",
            border_style="bright_blue",
            expand=True,
            show_lines=True,
        )

        # Add columns
        table.add_column(
            period_column_name, style=self.key_style, width=period_column_width
        )
        table.add_column("Models", style=self.value_style, width=20)
        table.add_column(
            "Input", style=self.value_style, justify="right", width=12
        )
        table.add_column(
            "Output", style=self.value_style, justify="right", width=12
        )
        table.add_column(
            "Cache Create", style=self.value_style, justify="right", width=12
        )
        table.add_column(
            "Cache Read", style=self.value_style, justify="right", width=12
        )
        table.add_column(
            "Total Tokens", style=self.accent_style, justify="right", width=12
        )
        table.add_column(
            "Cost (USD)", style=self.success_style, justify="right", width=10
        )

        return table

    def _add_data_rows(
        self,
        table: Table,
        data_list: list[TotalAggregatedData],
        period_key: str,
    ) -> None:
        """Add data rows to the table.

        Args:
            table: Table to add rows to
            data_list: List of data dictionaries
            period_key: Key to use for period column ('date' or 'month')
        """
        for data in data_list:
            # Safely extract models_used as a list of strings
            models_used = data.get("models_used", [])
            models_list = [str(object=model) for model in models_used if model]
            models_text = self._format_models(models_list)

            # Safely extract numeric values
            def safe_int(value: JSONSerializable) -> int:
                if isinstance(value, (int, float)):
                    return int(value)
                return 0

            total_tokens = (
                safe_int(data.get("input_tokens", 0))
                + safe_int(data.get("output_tokens", 0))
                + safe_int(data.get("cache_creation_tokens", 0))
                + safe_int(data.get("cache_read_tokens", 0))
            )

            # Safely extract period key value
            period_value = data.get(period_key, "")
            period_str = str(period_value) if period_value is not None else ""

            # Safely extract cost
            def safe_float(value: JSONSerializable) -> float:
                if isinstance(value, (int, float)):
                    return float(value)
                return 0.0

            table.add_row(
                period_str,
                models_text,
                format_number(safe_int(data.get("input_tokens", 0))),
                format_number(safe_int(data.get("output_tokens", 0))),
                format_number(safe_int(data.get("cache_creation_tokens", 0))),
                format_number(safe_int(data.get("cache_read_tokens", 0))),
                format_number(total_tokens),
                format_currency(safe_float(data.get("total_cost", 0.0))),
            )

    def _add_totals_row(self, table: Table, totals: AggregatedTotals) -> None:
        """Add totals row to the table.

        Args:
            table: Table to add totals to
            totals: Dictionary with total statistics
        """

        # Helper functions for safe type conversion
        def safe_int(value: JSONSerializable) -> int:
            if isinstance(value, (int, float)):
                return int(value)
            return 0

        def safe_float(value: JSONSerializable) -> float:
            if isinstance(value, (int, float)):
                return float(value)
            return 0.0

        # Add separator
        table.add_row("", "", "", "", "", "", "", "")

        # Add totals row
        table.add_row(
            Text("Total", style=self.accent_style),
            "",
            Text(
                format_number(safe_int(totals.get("input_tokens", 0))),
                style=self.accent_style,
            ),
            Text(
                format_number(safe_int(totals.get("output_tokens", 0))),
                style=self.accent_style,
            ),
            Text(
                format_number(safe_int(totals.get("cache_creation_tokens", 0))),
                style=self.accent_style,
            ),
            Text(
                format_number(safe_int(totals.get("cache_read_tokens", 0))),
                style=self.accent_style,
            ),
            Text(
                format_number(safe_int(totals.get("total_tokens", 0))),
                style=self.accent_style,
            ),
            Text(
                format_currency(safe_float(totals.get("total_cost", 0.0))),
                style=self.success_style,
            ),
        )

    def create_daily_table(
        self,
        daily_data: list[TotalAggregatedData],
        totals: AggregatedTotals,
        timezone: str = "UTC",
    ) -> Table:
        """Create a daily statistics table.

        Args:
            daily_data: List of daily aggregated data
            totals: Total statistics
            timezone: Timezone for display

        Returns:
            Rich Table object
        """
        # Create base table
        table = self._create_base_table(
            title=f"Claude Code Token Usage Report - Daily ({timezone})",
            period_column_name="Date",
            period_column_width=12,
        )

        # Add data rows
        self._add_data_rows(table, daily_data, "date")

        # Add totals
        self._add_totals_row(table, totals)

        return table

    def create_monthly_table(
        self,
        monthly_data: list[TotalAggregatedData],
        totals: AggregatedTotals,
        timezone: str = "UTC",
    ) -> Table:
        """Create a monthly statistics table.

        Args:
            monthly_data: List of monthly aggregated data
            totals: Total statistics
            timezone: Timezone for display

        Returns:
            Rich Table object
        """
        # Create base table
        table = self._create_base_table(
            title=f"Claude Code Token Usage Report - Monthly ({timezone})",
            period_column_name="Month",
            period_column_width=10,
        )

        # Add data rows
        self._add_data_rows(table, monthly_data, "month")

        # Add totals
        self._add_totals_row(table, totals)

        return table

    def create_summary_panel(
        self, view_type: str, totals: AggregatedTotals, period: str
    ) -> Panel:
        """Create a summary panel for the table view.

        Args:
            view_type: Type of view ('daily' or 'monthly')
            totals: Total statistics
            period: Period description

        Returns:
            Rich Panel object
        """

        # Helper functions for safe type conversion
        def safe_int(value: JSONSerializable) -> int:
            if isinstance(value, (int, float)):
                return int(value)
            return 0

        def safe_float(value: JSONSerializable) -> float:
            if isinstance(value, (int, float)):
                return float(value)
            return 0.0

        # Create summary text
        summary_lines = [
            f"📊 {view_type.capitalize()} Usage Summary - {period}",
            "",
            f"Total Tokens: {format_number(safe_int(totals.get('total_tokens', 0)))}",
            f"Total Cost: {format_currency(safe_float(totals.get('total_cost', 0.0)))}",
            f"Entries: {format_number(safe_int(totals.get('entries_count', 0)))}",
        ]

        summary_text = Text("\n".join(summary_lines), style=self.value_style)

        # Create panel
        panel = Panel(
            Align.center(summary_text),
            title="Summary",
            title_align="center",
            border_style=self.border_style,
            expand=False,
            padding=(1, 2),
        )

        return panel

    def _format_models(self, models: list[str]) -> str:
        """Format model names for display.

        Args:
            models: List of model names

        Returns:
            Formatted string of model names
        """
        if not models:
            return "No models"

        # Create bullet list
        if len(models) == 1:
            return models[0]
        elif len(models) <= 3:
            return "\n".join([f"• {model}" for model in models])
        else:
            # Truncate long lists
            first_two = models[:2]
            remaining_count = len(models) - 2
            formatted = "\n".join([f"• {model}" for model in first_two])
            formatted += f"\n• ...and {remaining_count} more"
            return formatted

    def create_no_data_display(self, view_type: str) -> Panel:
        """Create a display for when no data is available.

        Args:
            view_type: Type of view ('daily' or 'monthly')

        Returns:
            Rich Panel object
        """
        message = Text(
            f"No {view_type} data found.\n\nTry using Claude Code to generate some usage data.",
            style=self.warning_style,
            justify="center",
        )

        panel = Panel(
            Align.center(message, vertical="middle"),
            title=f"No {view_type.capitalize()} Data",
            title_align="center",
            border_style=self.warning_style,
            expand=True,
            height=10,
        )

        return panel

    def create_aggregate_table(
        self,
        aggregate_data: list[TotalAggregatedData],
        totals: AggregatedTotals,
        view_type: str,
        timezone: str = "UTC",
    ) -> Table:
        """Create a table for either daily or monthly aggregated data.

        Args:
            aggregate_data: List of aggregated data (daily or monthly)
            totals: Total statistics
            view_type: Type of view ('daily' or 'monthly')
            timezone: Timezone for display

        Returns:
            Rich Table object

        Raises:
            ValueError: If view_type is not 'daily' or 'monthly'
        """
        if view_type == "daily":
            return self.create_daily_table(aggregate_data, totals, timezone)
        elif view_type == "monthly":
            return self.create_monthly_table(aggregate_data, totals, timezone)
        else:
            raise ValueError(f"Invalid view type: {view_type}")

    def display_aggregated_view(
        self,
        data: list[TotalAggregatedData],
        view_mode: str,
        timezone: str,
        plan: str,
        token_limit: int,
        console: Console | None = None,
    ) -> None:
        """Display aggregated view with table and summary.

        Args:
            data: Aggregated data
            view_mode: View type ('daily' or 'monthly')
            timezone: Timezone string
            plan: Plan type
            token_limit: Token limit for the plan
            console: Optional Console instance
        """
        if not data:
            no_data_display = self.create_no_data_display(view_mode)
            if console:
                console.print(no_data_display)
            else:
                print(no_data_display)
            return

        # Helper function for safe numeric extraction
        def safe_numeric(value: JSONSerializable) -> float:
            if isinstance(value, (int, float)):
                return float(value)
            return 0.0

        # Calculate totals with safe type conversion
        # #TODO-ref: use a clearer approach for calculating totals
        totals = {
            "input_tokens": sum(
                safe_numeric(d.get("input_tokens", 0)) for d in data
            ),
            "output_tokens": sum(
                safe_numeric(d.get("output_tokens", 0)) for d in data
            ),
            "cache_creation_tokens": sum(
                safe_numeric(d.get("cache_creation_tokens", 0)) for d in data
            ),
            "cache_read_tokens": sum(
                safe_numeric(d.get("cache_read_tokens", 0)) for d in data
            ),
            "total_tokens": sum(
                safe_numeric(d.get("input_tokens", 0))
                + safe_numeric(d.get("output_tokens", 0))
                + safe_numeric(d.get("cache_creation_tokens", 0))
                + safe_numeric(d.get("cache_read_tokens", 0))
                for d in data
            ),
            "total_cost": sum(
                safe_numeric(d.get("total_cost", 0)) for d in data
            ),
            "entries_count": sum(
                safe_numeric(d.get("entries_count", 0)) for d in data
            ),
        }

        # Determine period for summary
        if view_mode == "daily":
            if data:
                start_date = str(data[0].get("date", "Unknown"))
                end_date = str(data[-1].get("date", "Unknown"))
                period = f"{start_date} to {end_date}"
            else:
                period = "No data"
        else:  # monthly
            if data:
                start_month = str(data[0].get("month", "Unknown"))
                end_month = str(data[-1].get("month", "Unknown"))
                period = f"{start_month} to {end_month}"
            else:
                period = "No data"

        # Create and display summary panel
        # Cast totals to AggregatedTotals
        json_totals = AggregatedTotals(
            {
                "input_tokens": int(totals["input_tokens"]),
                "output_tokens": int(totals["output_tokens"]),
                "cache_creation_tokens": int(totals["cache_creation_tokens"]),
                "cache_read_tokens": int(totals["cache_read_tokens"]),
                "total_tokens": int(totals["total_tokens"]),
                "total_cost": float(totals["total_cost"]),
                "entries_count": int(totals["entries_count"]),
            }
        )
        summary_panel = self.create_summary_panel(
            view_mode, json_totals, period
        )

        # Create and display table
        table = self.create_aggregate_table(
            data, json_totals, view_mode, timezone
        )

        # Display using console if provided
        if console:
            console.print(summary_panel)
            console.print()
            console.print(table)
        else:
            from rich import print as rprint

            rprint(summary_panel)
            rprint()
            rprint(table)
