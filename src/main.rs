mod analyzer;
mod repo;
mod tool;

use quicli::prelude::*;
use structopt::StructOpt;

fn main() -> CliResult {
    let args = Cli::from_args();

    let repo_file = read_file(&args.input_path)?;
    let repos: Vec<&str> = repo_file.lines().take(args.repo_count).collect();

    analyzer::analyze(repos).unwrap_or_else(|err| eprintln!("{}", err));

    Ok(())
}

#[derive(Debug, StructOpt)]
struct Cli {
    #[structopt(
        long = "input_path",
        short = "p",
        default_value = "./data/in/awesome-rust.txt"
    )]
    input_path: String,
    #[structopt(long = "repo_count", short = "c", default_value = "1")]
    repo_count: usize,
}
