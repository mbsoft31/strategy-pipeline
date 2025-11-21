"""
Search command for querying academic databases.

This command executes searches across configured providers.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click

from slr.cli.formatting import (
    console,
    create_progress,
    format_duration,
    format_number,
    print_config,
    print_error,
    print_header,
    print_provider_results,
    print_success,
    print_warning,
)
from slr.cli.main import pass_context
from slr.cli.utils import (
    generate_run_id,
    load_config,
    load_queries,
    save_documents,
    save_metadata,
)
from slr.core.config import ProviderConfig
from slr.core.models import Query
from slr.providers import get_provider


@click.command()
@click.option(
    "--queries",
    type=click.Path(exists=True, path_type=Path),
    help="Path to queries file (YAML/JSON)",
)
@click.option(
    "--query",
    type=str,
    help="Single query string (quick search)",
)
@click.option(
    "--query-id",
    type=str,
    help="Search specific query ID from queries file",
)
@click.option(
    "--provider",
    multiple=True,
    help="Specific provider(s) to use (can repeat)",
)
@click.option(
    "--skip-provider",
    multiple=True,
    help="Provider(s) to skip",
)
@click.option(
    "--year-min",
    type=int,
    help="Minimum publication year",
)
@click.option(
    "--year-max",
    type=int,
    help="Maximum publication year",
)
@click.option(
    "--max-results",
    type=int,
    help="Maximum results per query (per provider)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=Path("outputs"),
    help="Output directory",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "jsonl", "both"], case_sensitive=False),
    default="both",
    help="Output format",
)
@click.option(
    "--run-id",
    type=str,
    help="Custom run identifier",
)
@click.option(
    "--resume",
    is_flag=True,
    help="Resume interrupted search",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be searched without executing",
)
@pass_context
def search(
    ctx,
    queries: Optional[Path],
    query: Optional[str],
    query_id: Optional[str],
    provider: tuple,
    skip_provider: tuple,
    year_min: Optional[int],
    year_max: Optional[int],
    max_results: Optional[int],
    output: Path,
    output_format: str,
    run_id: Optional[str],
    resume: bool,
    dry_run: bool,
):
    """Search academic databases.

    Execute searches across configured providers and save results.

    \b
    Examples:
      # Search with queries file
      slr search --queries queries.yml

      # Quick single query search
      slr search --query "machine learning AND agriculture"

      # Search specific providers only
      slr search --queries queries.yml --provider openalex --provider arxiv

      # Search with filters
      slr search --queries queries.yml --year-min 2020 --max-results 500
    """
    start_time = time.time()

    print_header("Simple SLR Search", "Multi-provider academic database search")

    # Load configuration
    config = load_config(ctx.config_path)

    # Override config with CLI options
    if year_min is not None:
        config.year_min = year_min
    if year_max is not None:
        config.year_max = year_max

    # Determine queries to search
    queries_dict = {}
    if query:
        # Single query from command line
        queries_dict = {"cli_query": [query]}
    elif queries:
        # Load from file
        queries_dict = load_queries(queries)
        if query_id:
            # Filter to specific query ID
            if query_id not in queries_dict:
                print_error(f"Query ID '{query_id}' not found in queries file")
                raise click.Abort()
            queries_dict = {query_id: queries_dict[query_id]}
    else:
        print_error("Either --queries or --query must be specified")
        raise click.Abort()

    # Flatten queries for processing
    all_queries = []
    query_counter = 1
    for category, query_list in queries_dict.items():
        for q in query_list:
            all_queries.append({
                "id": f"Q{query_counter:02d}",
                "category": category,
                "text": q,
            })
            query_counter += 1

    if not all_queries:
        print_error("No queries to search")
        raise click.Abort()

    # Determine which providers to use
    enabled_providers = []
    if provider:
        # Use specified providers
        enabled_providers = list(provider)
    else:
        # Use all enabled providers from config
        for prov_name in ["openalex", "crossref", "arxiv", "semantic_scholar"]:
            prov_config = config.providers.get_provider(prov_name)
            if prov_config and prov_config.enabled:
                enabled_providers.append(prov_name)

    # Remove skipped providers
    if skip_provider:
        enabled_providers = [p for p in enabled_providers if p not in skip_provider]

    if not enabled_providers:
        print_error("No providers enabled")
        raise click.Abort()

    # Generate run ID
    if not run_id:
        run_id = generate_run_id()

    # Set up output directory
    output_dir = output / run_id

    # Print configuration
    print_config({
        "Queries": f"{len(all_queries)} queries from {len(queries_dict)} categories",
        "Providers": ", ".join(enabled_providers),
        "Year range": f"{config.year_min or 'any'}-{config.year_max or 'current'}",
        "Max results": max_results or "unlimited",
        "Output": str(output_dir),
    })

    if dry_run:
        console.print("\n[yellow]DRY RUN - No searches will be executed[/yellow]\n")
        console.print("[bold]Queries to be executed:[/bold]")
        for q in all_queries:
            console.print(f"  {q['id']} ({q['category']}): {q['text']}")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Execute searches
    provider_results: Dict[str, int] = {}

    for provider_name in enabled_providers:
        console.print(f"\n[bold cyan]Searching {provider_name}...[/bold cyan]")

        # Get provider config
        prov_config = config.providers.get_provider(provider_name)
        if not prov_config:
            prov_config = ProviderConfig()

        # Override mailto if set in main config
        if config.mailto:
            prov_config.mailto = config.mailto

        # Create provider instance
        try:
            provider_instance = get_provider(provider_name, prov_config)
        except Exception as e:
            print_error(f"Failed to initialize {provider_name}: {e}")
            continue

        # Create provider output directory
        provider_dir = output_dir / provider_name
        provider_dir.mkdir(exist_ok=True)

        # Search each query
        provider_total = 0
        all_provider_docs = []

        with create_progress() as progress:
            task = progress.add_task(
                f"[cyan]{provider_name}[/cyan]",
                total=len(all_queries)
            )

            for q_info in all_queries:
                # Create Query object
                query_obj = Query(
                    text=q_info["text"],
                    year_min=config.year_min,
                    year_max=config.year_max,
                    max_results=max_results,
                )

                # Execute search
                try:
                    docs = list(provider_instance.search(query_obj))

                    # Save per-query results
                    query_file = provider_dir / f"{q_info['id']}_results.jsonl"
                    save_documents(docs, query_file, format="jsonl")

                    all_provider_docs.extend(docs)
                    provider_total += len(docs)

                    progress.console.print(
                        f"  {q_info['id']}: {q_info['text'][:50]}... "
                        f"[green]{len(docs)} results[/green]"
                    )

                except Exception as e:
                    progress.console.print(
                        f"  {q_info['id']}: [red]Error: {e}[/red]"
                    )

                progress.update(task, advance=1)

        # Save aggregated results
        all_results_file = provider_dir / "all_results.jsonl"
        save_documents(all_provider_docs, all_results_file, format="jsonl")

        # Save CSV if requested
        if output_format in ("csv", "both"):
            csv_file = provider_dir / "all_results.csv"
            save_documents(all_provider_docs, csv_file, format="csv")

        provider_results[provider_name] = provider_total
        print_success(f"{provider_name}: {format_number(provider_total)} documents")

    # Save metadata
    metadata = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "queries": all_queries,
        "providers": enabled_providers,
        "config": {
            "year_min": config.year_min,
            "year_max": config.year_max,
            "max_results": max_results,
        },
        "results": provider_results,
    }
    save_metadata(output_dir, metadata)

    # Save summary
    summary_lines = [
        f"Simple SLR Search Results",
        f"=" * 70,
        f"",
        f"Run ID: {run_id}",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"Queries: {len(all_queries)} queries from {len(queries_dict)} categories",
        f"Providers: {', '.join(enabled_providers)}",
        f"",
        f"Results by Provider:",
    ]

    total_docs = 0
    for prov_name, count in provider_results.items():
        summary_lines.append(f"  {prov_name}: {count:,} documents")
        total_docs += count

    summary_lines.extend([
        f"",
        f"Total: {total_docs:,} documents",
        f"Duration: {format_duration(time.time() - start_time)}",
    ])

    summary_path = output_dir / "summary.txt"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    # Print final summary
    console.print()
    console.rule()
    print_success("Search complete!")
    console.print()
    print_provider_results(provider_results)
    console.print()
    console.print(f"  Output: [cyan]{output_dir}[/cyan]")
    console.print(f"  Duration: [cyan]{format_duration(time.time() - start_time)}[/cyan]")
    console.print()

