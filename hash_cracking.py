import shutil
import subprocess
from time import time
import pandas as pd
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from typing import Optional

console = Console()

def detect_tools():
    tools = {}
    tools['hashcat'] = shutil.which('hashcat') is not None
    tools['john'] = shutil.which('john') is not None
    return tools

def choose_tool(tools):
    console.print("[bold]Available Cracking Tools:[/bold]")
    for i, tool in enumerate(tools, 1):
        console.print(f"{i}) {tool} {'(installed)' if tools[tool] else '(not installed)'}")
    console.print()

    while True:
        choice = Prompt.ask("Select a tool", choices=[str(i+1) for i in range(len(tools))], default="1")
        tool_name = list(tools.keys())[int(choice) - 1]
        if tools[tool_name]:
            return tool_name
        console.print("[red]Selected tool is not installed. Please choose again.[/red]")

def get_hash_type():
    return Prompt.ask("Enter hash type or leave empty for auto-detect", default="")

def get_wordlist():
    return Prompt.ask("Enter path to wordlist", default="rockyou.txt")

def spawn_cracking_tool(tool: str, hash_file: str, hash_type: Optional[str], wordlist: str):
    command = []
    if tool == 'hashcat':
        command = ['hashcat', '-m', hash_type, hash_file, wordlist] if hash_type else ['hashcat', hash_file, wordlist]
    elif tool == 'john':
        command = ['john', f'--wordlist={wordlist}', hash_file]
    return command

def capture_output(command):
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as process:
        with Live(console=console, auto_refresh=False) as live:
            panel = Panel("Initializing...", title="Cracking", border_style="green")
            live.update(panel)
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                panel = Panel(line.strip(), title="Cracking", border_style="green")
                live.update(panel)
                console.refresh()
            process.wait()

    return process.returncode

def parse_output(tool: str, hash_file: str, duration: float) -> pd.DataFrame:
    # Pseudo-implementation: Replace with parsing logic specific to each tool
    data = [
        {"hash": "example_hash1", "plaintext": "example_password1", "tool": tool, "duration": duration},
        {"hash": "example_hash2", "plaintext": "example_password2", "tool": tool, "duration": duration}
    ]
    return pd.DataFrame(data)

def main():
    tools = detect_tools()
    if not any(tools.values()):
        console.print("[red]No cracking tools installed. Exiting.[/red]")
        return

    tool = choose_tool(tools)
    hash_type = get_hash_type()
    wordlist = get_wordlist()

    # Placeholder for hash file input
    hash_file = Prompt.ask("Enter path to hash file", default="hashes.txt")

    confirm = Confirm.ask(f"Proceed with {tool} using hash file {hash_file} with wordlist {wordlist}?", default=True)
    if not confirm:
        console.print("[yellow]Operation cancelled by user.[/yellow]")
        return

    start_time = time()
    command = spawn_cracking_tool(tool, hash_file, hash_type, wordlist)
    return_code = capture_output(command)
    end_time = time()

    if return_code == 0:
        duration = end_time - start_time
        df = parse_output(tool, hash_file, duration)
        console.print("[green]Cracking completed successfully.[/green]")
        console.print(df)
    else:
        console.print("[red]Cracking failed.[/red]")

if __name__ == "__main__":
    main()
