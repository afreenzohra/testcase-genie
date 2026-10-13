"""Command Line Interface for TestCase-Genie using Typer and Rich."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from testcase_genie import __version__
from testcase_genie.agent import (
    EmptyInputError,
    GeminiAgent,
    GeminiRateLimitError,
    GeminiServiceError,
    JSONParsingError,
    MissingAPIKeyError,
)
from testcase_genie.exporter import export_suite_to_files, suite_to_markdown
from testcase_genie.generator import TestCaseGenerator
from testcase_genie.models import FrameworkType, GenerationConfig, TestCaseSuite

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

app = typer.Typer(
    name="testcase-genie",
    help="TestCase-Genie: Generate structured QA test cases & POM automation code with Google Gemini.",
    add_completion=False,
)
console = Console(legacy_windows=False)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]TestCase-Genie[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


@app.command()
def generate(
    story: Optional[str] = typer.Argument(
        None,
        help="User story or requirement as a direct text string.",
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to a text (.txt) or markdown (.md) file containing the user story.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    framework: FrameworkType = typer.Option(
        FrameworkType.PLAYWRIGHT,
        "--framework",
        "-F",
        help="Target test automation framework: playwright or selenium.",
        case_sensitive=False,
    ),
    count: int = typer.Option(
        5,
        "--count",
        "-n",
        help="Target number of test cases to generate (1-30).",
        min=1,
        max=30,
    ),
    app_type: Optional[str] = typer.Option(
        None,
        "--app-type",
        "-t",
        help="Application domain (e.g. e-commerce, login, banking, healthcare).",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to save exported test cases (.json, .md, .csv) and test code (.py).",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Gemini model override (e.g. gemini-2.5-flash, gemini-2.5-pro).",
    ),
    show_code: bool = typer.Option(
        False,
        "--show-code",
        help="Display generated Python automation code directly in the terminal.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Generate structured QA test cases and starter automation code from a user story."""

    # 1. Resolve User Story Input
    user_story_text = ""
    if file:
        user_story_text = file.read_text(encoding="utf-8").strip()
    elif story:
        user_story_text = story.strip()
    else:
        # Prompt interactively if neither provided
        console.print("[bold yellow]No story provided via arguments or file.[/bold yellow]")
        user_story_text = typer.prompt("Please paste your user story / feature description").strip()

    if not user_story_text:
        console.print("[bold red]Error:[/bold red] User story cannot be empty.", style="red")
        raise typer.Exit(code=1)

    # 2. Configuration Setup
    config = GenerationConfig(
        framework=framework,
        test_count=count,
        app_type=app_type,
    )

    console.print(
        Panel.fit(
            f"[bold cyan]🧞 TestCase-Genie Agent[/bold cyan]\n"
            f"[dim]Framework:[/dim] [green]{framework.value.upper()}[/green] | "
            f"[dim]Target Cases:[/dim] [green]{count}[/green] | "
            f"[dim]Domain:[/dim] [yellow]{app_type or 'General'}[/yellow]",
            border_style="cyan",
        )
    )

    # 3. Execution Pipeline
    try:
        agent = GeminiAgent(model=model)
        generator = TestCaseGenerator(agent=agent)

        with console.status("[bold cyan]Analyzing user story & generating test suite with Gemini...[/bold cyan]", spinner="dots"):
            suite: TestCaseSuite = generator.generate(
                user_story=user_story_text,
                config=config,
            )

    except MissingAPIKeyError as e:
        console.print(
            Panel(
                f"[bold red]Authentication Missing[/bold red]\n\n"
                f"{str(e)}\n\n"
                f"[bold yellow]Quick Fix:[/bold yellow]\n"
                f"1. Copy [green].env.example[/green] to [green].env[/green]\n"
                f"2. Add your Gemini API key: [italic]GEMINI_API_KEY=your_key_here[/italic]\n"
                f"3. Get a free API key at [link=https://aistudio.google.com/]Google AI Studio[/link]",
                title="API Key Error",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)

    except EmptyInputError as e:
        console.print(f"[bold red]Input Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    except GeminiRateLimitError as e:
        console.print(
            Panel(
                f"[bold red]Rate Limit Exceeded[/bold red]\n\n{e}\n\n"
                f"Please wait a moment before running again or switch to a paid tier/different model.",
                title="Rate Limit",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)

    except (GeminiServiceError, JSONParsingError) as e:
        console.print(f"[bold red]Generation Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 4. Display Results Table
    console.print(f"\n[bold green]✓ Successfully generated {len(suite.test_cases)} test cases![/bold green]\n")

    table = Table(title=f"Test Suite: {suite.title}", header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Type", style="yellow", justify="center")
    table.add_column("Priority", style="bold", justify="center")
    table.add_column("Expected Outcome", style="dim white")

    type_styles = {
        "positive": "[green]POSITIVE[/green]",
        "negative": "[red]NEGATIVE[/red]",
        "edge": "[yellow]EDGE[/yellow]",
    }

    priority_styles = {
        "critical": "[bold red]CRITICAL[/bold red]",
        "high": "[bold orange3]HIGH[/bold orange3]",
        "medium": "[yellow]MEDIUM[/yellow]",
        "low": "[dim]LOW[/dim]",
    }

    for tc in suite.test_cases:
        t_key = tc.type.value if hasattr(tc.type, "value") else str(tc.type)
        p_key = tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)
        table.add_row(
            tc.id,
            tc.title,
            type_styles.get(t_key, t_key.upper()),
            priority_styles.get(p_key, p_key.upper()),
            tc.expected_result,
        )

    console.print(table)

    # 5. Display Code Preview if requested
    if show_code and suite.generated_code:
        console.print("\n[bold cyan]Automation Starter Code Preview (Page Object Model):[/bold cyan]")
        syntax = Syntax(suite.generated_code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)

    # 6. Export to Files if output_dir specified
    if output_dir:
        exported = export_suite_to_files(
            suite=suite,
            output_dir=output_dir,
            base_name=f"{suite.title.lower().replace(' ', '_')[:30]}",
        )
        console.print(f"\n[bold green]Exported assets to directory:[/bold green] [underline]{output_dir}[/underline]")
        for fmt, path in exported.items():
            console.print(f"  • [bold]{fmt.upper():<4}[/bold] -> {path.name}")
    else:
        console.print("\n[dim]Tip: Pass '--output-dir ./results' to export Markdown, JSON, CSV, and Python code files.[/dim]")


def main() -> None:
    """Entry point for the console script."""
    app()


if __name__ == "__main__":
    main()
