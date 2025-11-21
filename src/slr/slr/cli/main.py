"""
Main CLI entry point for Simple SLR.

This module provides the main CLI group and global options.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from src.slr.cli.formatting import console, print_error, print_header
from src.slr.cli.utils import setup_logging


# Version info
__version__ = "0.9.1-alpha.0"


# Global context object for passing config between commands
class CLIContext:
    """Context object for CLI commands."""

    def __init__(self):
        self.config_path: Optional[Path] = None
        self.verbose: int = 0
        self.quiet: bool = False


pass_context = click.make_pass_decorator(CLIContext, ensure=True)


@click.group()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file (default: config.yml)",
)
@click.option(
    "--verbose", "-v",
    count=True,
    help="Enable verbose logging (can be repeated: -vv, -vvv)",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress non-error output",
)
@click.version_option(version=__version__, prog_name="Simple SLR")
@click.pass_context
def cli(ctx, config: Optional[Path], verbose: int, quiet: bool):
    """
    Simple SLR - Systematic Literature Review Framework

    A modern, extensible framework for conducting systematic literature reviews
    with support for multiple academic databases, intelligent deduplication,
    and PRISMA-compliant workflows.

    \b
    Typical workflow:
      1. slr init              # Set up project structure
      2. slr search            # Search academic databases
      3. slr deduplicate       # Remove duplicates
      4. slr export            # Export to BibTeX/CSV/etc.

    \b
    For help on a specific command:
      slr <command> --help
    """
    # Initialize context
    cli_ctx = ctx.ensure_object(CLIContext)
    cli_ctx.config_path = config
    cli_ctx.verbose = verbose
    cli_ctx.quiet = quiet

    # Set up logging
    setup_logging(verbose=verbose, quiet=quiet)


# Import and register commands
# This must happen at module level so commands are available when cli() is called
from src.slr.cli.init import init
from src.slr.cli.search import search
from src.slr.cli.deduplicate import deduplicate
from src.slr.cli.export import export
from src.slr.cli.validate import validate

cli.add_command(init)
cli.add_command(search)
cli.add_command(deduplicate)
cli.add_command(export)
cli.add_command(validate)


def main():
    """Main entry point for the CLI."""
    try:
        # Run CLI
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()

