from ast import literal_eval

import cmd2
from rich.console import Console
from rich.table import Table

from moonshot.api import api_get_all_run
from moonshot.integrations.cli.common.display_helper import (
    display_view_list_format,
    display_view_str_format,
)
from moonshot.integrations.cli.utils.process_data import filter_data

console = Console()


# ------------------------------------------------------------------------------
# CLI Functions
# ------------------------------------------------------------------------------
def list_runs(args) -> list | None:
    """
    List all runs.

    This function retrieves all available runs by calling the api_get_all_run function from the
    moonshot.api module. It then calls the display_runs function to present the retrieved run information
    in a user-friendly format on the command line interface. If an exception occurs during the retrieval
    or display process, it prints an error message.

    Args:
        args: A namespace object from argparse. It should have an optional attribute:
        find (str): Optional field to find run(s) with a keyword.
        pagination (str): Optional field to paginate runs.

    Returns:
        list | None: A list of Run or None if there is no result.
    """

    try:
        runner_run_info = api_get_all_run()
        keyword = args.find.lower() if args.find else ""
        pagination = literal_eval(args.pagination) if args.pagination else ()

        if runner_run_info:
            filtered_runs_list = filter_data(runner_run_info, keyword, pagination)
            if filtered_runs_list:
                display_runs(filtered_runs_list)
                return filtered_runs_list

        console.print("[red]There are no runs found.[/red]")
        return None

    except Exception as e:
        print(f"[list_runs]: {str(e)}")


def view_run(args) -> None:
    """
    View the details of a specific run.

    This function retrieves and displays information about a specific run associated with a runner. It uses the runner
    identifier provided in the arguments to fetch the data and then calls the display_runs function to present it in a
    user-friendly format.

    Args:
        args: A namespace object from argparse. It should have the following attribute:
            runner (str): The identifier of the runner whose runs are to be viewed.

    Returns:
        None
    """
    try:
        runner_run_info = api_get_all_run(args.runner_id)
        display_runs(runner_run_info)
    except Exception as e:
        print(f"[view_run]: {str(e)}")


# ------------------------------------------------------------------------------
# Helper functions: Display on cli
# ------------------------------------------------------------------------------
def display_runs(runs_list: list):
    """
    Display a list of runs in a table format.

    This function takes a list of run information and displays it in a table format using the rich library's
    Table object.

    Each run's details are formatted and added as a row in the table.
    If there are no runs to display, a message is printed to indicate that no results were found.

    Args:
        runs_list (list): A list of dictionaries, where each dictionary contains details of a run.

    Returns:
        None
    """
    table = Table(
        title="List of Runs", show_lines=True, expand=True, header_style="bold"
    )
    table.add_column("No.", width=2)
    table.add_column("Run", justify="left", width=78)
    table.add_column("Contains", justify="left", width=20, overflow="fold")
    for idx, run in enumerate(runs_list, 1):
        (
            run_id,
            runner_id,
            runner_type,
            runner_args,
            endpoints,
            results_file,
            start_time,
            end_time,
            duration,
            error_messages,
            raw_results,
            results,
            status,
            *other_args,
        ) = run.values()

        duration_info = f"[blue]Period:[/blue] {start_time} - {end_time} ({duration}s)"
        run_id = display_view_str_format("Run ID", run_id)
        runner_id = display_view_str_format("Runner ID", runner_id)
        runner_type = display_view_str_format("Runner Type", runner_type)
        runner_args = display_view_str_format("Runner Args", runner_args)
        status_info = display_view_str_format("Status", status)
        results_info = display_view_str_format("Results File", results_file)
        endpoints_info = display_view_list_format("Endpoints", endpoints)
        error_messages_info = display_view_list_format("Error Messages", error_messages)

        has_raw_results = bool(raw_results)
        has_results = bool(results)
        idx = run.get("idx", idx)

        result_info = (
            f"[red]{runner_id}[/red]\n\n{run_id}\n\n{duration_info}\n\n{status_info}"
        )
        contains_info = (
            f"{results_info}\n\n{error_messages_info}\n\n{endpoints_info}\n\n"
            f"[blue]Has Raw Results: {has_raw_results}[/blue]\n\n"
            f"[blue]Has Results: {has_results}[/blue]"
        )

        table.add_section()
        table.add_row(str(idx), result_info, contains_info)
    console.print(table)


# ------------------------------------------------------------------------------
# Cmd2 Arguments Parsers
# ------------------------------------------------------------------------------
# View run arguments
view_run_args = cmd2.Cmd2ArgumentParser(
    description="View a runner runs.",
    epilog="Example:\n view_run my-new-cookbook-runner",
)
view_run_args.add_argument("runner_id", type=str, help="Name of the runner")


# List run arguments
list_runs_args = cmd2.Cmd2ArgumentParser(
    description="List all runs.",
    epilog='Example:\n list_runs -f "my-run"',
)

list_runs_args.add_argument(
    "-f",
    "--find",
    type=str,
    help="Optional field to find run(s) with keyword",
    nargs="?",
)

list_runs_args.add_argument(
    "-p",
    "--pagination",
    type=str,
    help="Optional tuple to paginate run(s). E.g. (2,10) returns 2nd page with 10 items in each page.",
    nargs="?",
)
