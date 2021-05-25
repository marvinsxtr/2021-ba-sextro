pub mod analyzer;

use quicli::prelude::*;
use structopt::StructOpt;

fn main() -> CliResult {
    let args = Cli::from_args();

    let repo_file = read_file(&args.path)?;
    let repos: Vec<&str> = repo_file.lines().take(args.count).collect();
    
    analyzer::analyze(repos).unwrap_or_else(|err| {
        eprintln!("{:?}", err)
    });

    Ok(())
}

#[derive(Debug, StructOpt)]
struct Cli {
    #[structopt(long = "path", short = "p", default_value = "./data/awesome-rust.txt")]
    path: String,
    #[structopt(long = "count", short = "c", default_value = "1")]
    count: usize,
}
