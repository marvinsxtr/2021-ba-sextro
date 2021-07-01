mod analyzer;
mod finding;
mod repo;
mod tool;
mod utils;
mod metrics;
mod out;
mod src;

use quicli::prelude::*;
use structopt::StructOpt;

fn main() -> CliResult {
    let args = Cli::from_args();

    let repo_file = read_file(&args.input_path)?;
    let repos: Vec<&str> = repo_file.lines().take(args.repo_count).collect();

    analyzer::analyze(repos, &args).unwrap_or_else(|err| eprintln!("{}", err));

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
    #[structopt(long = "analyze_only", short = "a")]
    analyze_only: bool,
    #[structopt(long = "delete_tmp", short = "d")]
    delete_tmp: bool,
}
