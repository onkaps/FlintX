mod commands;

use clap::{Parser, Subcommand};
use colored::Colorize;

#[derive(Parser)]
#[command(
    name = "flintx",
    version = "0.1.0",
    author = "Flint-X Team",
    about = "AI-driven performance intelligence tool aligned with AMD hardware"
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize a new Flint-X project in the current directory
    Init,

    /// Run static analysis on a Python source file
    Analyze {
        /// Path to the Python file or directory to analyze
        #[arg(short, long)]
        target: String,
    },

    /// Profile runtime performance of a Python script
    Profile {
        /// Path to the Python script to profile
        #[arg(short, long)]
        target: String,
    },

    /// Query the AI layer for optimization recommendations
    Optimize {
        /// Path to a pre-generated analysis JSON file (optional)
        #[arg(short, long)]
        input: Option<String>,
    },

    /// Run the full Flint-X pipeline: analyze → profile → optimize
    Run {
        /// Path to the Python file to run the full pipeline on
        #[arg(short, long)]
        target: String,
    },
}

fn main() {
    print_banner();
    let cli = Cli::parse();

    match cli.command {
        Commands::Init => commands::init::execute(),
        Commands::Analyze { target } => commands::analyze::execute(&target),
        Commands::Profile { target } => commands::profile::execute(&target),
        Commands::Optimize { input } => commands::optimize::execute(input),
        Commands::Run { target } => commands::run::execute(&target),
    }
}

fn print_banner() {
    println!("{}", "╔══════════════════════════════════════╗".cyan());
    println!("{}", "║        Flint-X v0.1.0                ║".cyan());
    println!("{}", "║  AI Performance Intelligence Tool    ║".cyan());
    println!("{}", "║  AMD Hardware-Aware Optimization     ║".cyan());
    println!("{}", "╚══════════════════════════════════════╝".cyan());
    println!();
}