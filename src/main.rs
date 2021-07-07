mod analyzer;
mod finding;
mod out;
mod repo;
mod src;
mod tool;
mod utils;

use quicli::prelude::*;
use structopt::StructOpt;

fn main() -> CliResult {
    let args = Cli::from_args();

    let repo_file = read_file(&args.input_path)?;
    let repos: Vec<&str> = repo_file.lines().skip(args.repo_skips).take(args.repo_count).collect();

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
    #[structopt(long = "repo_count", short = "n", default_value = "1")]
    repo_count: usize,
    #[structopt(long = "repo_skips", short = "s", default_value = "0")]
    repo_skips: usize,
    #[structopt(long = "clone_repos", short = "c")]
    clone: bool,
    #[structopt(long = "collect_metrics", short = "m")]
    metrics: bool,
    #[structopt(long = "filter_metrics", short = "f")]
    filter: bool,
    #[structopt(long = "delete_tmp", short = "d")]
    delete: bool,
}
