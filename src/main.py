import os
import sys

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import click
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from kb.loader import KnowledgeBaseLoader
from kb.qa import KnowledgeBaseQA

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()

@click.group()
def cli():
    """Local Knowledge Base CLI with Deepseek API"""
    pass

@cli.command()
@click.option('--kb-dir', '-k', required=True, help='Path to knowledge base directory containing .md files')
@click.option('--persist-dir', '-p', default='./chroma_db', help='Path to persist vector store')
@click.option('--api-key', '-a', help='Deepseek API key (optional, uses .env if not provided)')
def build(kb_dir, persist_dir, api_key):
    """Build knowledge base from markdown files"""
    try:
        console.print(Panel("[bold green]Building Knowledge Base[/bold green]", expand=False))
        
        # Check if kb_dir exists
        if not os.path.exists(kb_dir):
            console.print(f"[bold red]Error:[/bold red] Knowledge base directory '{kb_dir}' does not exist.")
            return
        
        # Check if there are .md files
        md_files = list(Path(kb_dir).glob("*.md"))
        if not md_files:
            console.print(f"[bold red]Error:[/bold red] No markdown files found in '{kb_dir}'.")
            return
        
        # Initialize loader
        loader = KnowledgeBaseLoader(kb_dir, persist_dir, api_key)
        
        # Build knowledge base
        loader.build_knowledge_base()
        
        console.print(Panel("[bold green]✓ Knowledge Base Built Successfully![/bold green]", expand=False))
        console.print(f"[bold blue]Vector store saved at:[/bold blue] {persist_dir}")
        console.print(f"[bold blue]Documents processed:[/bold blue] {len(md_files)}")
        
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {str(e)}", expand=False))

@cli.command()
def chat():
    """Interactive chat with the knowledge base"""
    try:
        console.print(Panel("[bold green]Starting Knowledge Base Chat[/bold green]", expand=False))
        
        # Load vector store
        console.print("Loading knowledge base...")
        loader = KnowledgeBaseLoader("./", "./chroma_db")
        vector_store = loader.load_vector_store()
        
        # Initialize QA system
        qa = KnowledgeBaseQA(vector_store)
        
        console.print("\n[bold blue]Knowledge Base is ready![/bold blue]")
        console.print("Type 'exit' or 'quit' to end the chat.\n")
        
        while True:
            question = Prompt.ask("[bold yellow]You[/bold yellow]")
            
            if question.lower() in ['exit', 'quit', 'q']:
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            
            if not question.strip():
                continue
            
            console.print("\n[bold blue]AI[/bold blue]: ", end="")
            
            try:
                result = qa.ask_question(question)
                
                # Display answer
                console.print(Markdown(result["answer"]))
                
                # Display sources
                if result["sources"]:
                    console.print("\n[bold blue]Sources:[/bold blue]")
                    for source in set(result["sources"]):  # Remove duplicates
                        console.print(f"  - {Path(source).name}")
                
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
            
            console.print("")
            
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {str(e)}", expand=False))
        console.print("[bold yellow]Hint:[/bold yellow] Make sure you have built the knowledge base first using 'build' command.")

@cli.command()
@click.argument('question')
@click.option('--answer-only', '-a', is_flag=True, help='Only return the answer without sources')
def ask(question, answer_only):
    """Ask a single question to the knowledge base"""
    try:
        # Load vector store
        loader = KnowledgeBaseLoader("./", "./chroma_db")
        vector_store = loader.load_vector_store()
        
        # Initialize QA system
        qa = KnowledgeBaseQA(vector_store)
        
        # Get answer
        result = qa.ask_question(question, answer_only=answer_only)
        
        # Display result
        console.print(Panel("[bold blue]Answer[/bold blue]", expand=False))
        if isinstance(result, str):
            # If answer_only is True, result is just the answer string
            console.print(Markdown(result))
        else:
            # Normal case with answer and sources
            console.print(Markdown(result["answer"]))
            
            # Display sources if available
            if result["sources"]:
                console.print("\n[bold blue]Sources:[/bold blue]")
                for source in set(result["sources"]):
                    console.print(f"  - {Path(source).name}")
                    
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {str(e)}", expand=False))
        console.print("[bold yellow]Hint:[/bold yellow] Make sure you have built the knowledge base first using 'build' command.")

if __name__ == "__main__":
    cli()
