mod collector;
mod finding;
mod out;
mod repo;
mod src;
mod tool;
mod utils;

use collector::CollectorTask;
use indicatif::{ProgressBar, ProgressStyle};
use log::info;
use quicli::prelude::*;
use structopt::StructOpt;
use utils::setup_logger;

/// Run the command line interface of the `collector`.
fn main() -> CliResult {
    setup_logger().unwrap_or_else(|err| eprintln!("Failed to initialize logger: {}", err));
    info!("Starting the collector");

    let args = Cli::from_args();

    let repo_file = read_file(&args.input_path)?;
    let repos: Vec<&str> = repo_file
        .lines()
        .skip(args.repo_skips)
        .take(args.repo_count)
        .collect();

    let mut tasks: Vec<CollectorTask> = Vec::new();

    if args.clone {
        tasks.push(CollectorTask::CloneRepos);
    }
    if args.metrics {
        tasks.push(CollectorTask::CollectMetrics);
    }
    if args.filter {
        tasks.push(CollectorTask::FilterMetrics);
    }
    if args.delete {
        tasks.push(CollectorTask::DeleteTmp);
    }

    let sty = ProgressStyle::default_bar()
        .template(
            "[{elapsed_precise}]  [{wide_bar:.cyan/blue}]  Task {pos:>2}/{len:2}    Batch \
             {msg:>2}    ETA {eta:>1}",
        )
        .progress_chars("#>-");
    let progress_bar = ProgressBar::new(repos.len() as u64 * tasks.len() as u64)
        .with_style(sty)
        .with_message("0/?");
    progress_bar.enable_steady_tick(1000);

    let batches = repos.chunks(args.batch_size);
    let num_batches = batches.len();

    for (i, batch) in batches.into_iter().enumerate() {
        progress_bar.set_message(format!("{}/{}", i + 1, num_batches));
        for task in &tasks {
            collector::collect(batch.to_vec(), task, &progress_bar)
                .unwrap_or_else(|err| error!("Failed to run task on batch: {}", err));
        }
    }

    progress_bar.finish();
    info!("Done with {} repositories", repos.len());

    Ok(())
}

/// This struct contains all arguments which can be passed to the `collector`
/// CLI. They can be used to define a pipeline with each stage being one
/// optional flag. The base path of the mentioned output folders can be
/// specified using the `DATA_PATH` environment variable.
///
/// # Examples
///
/// ```sh
/// ./collector -n 3 -s 3 -c -m -f -d
/// ```
///
/// This command runs on the 4th to 6th repository on the `awesome-rust` list
/// and **c**lones them, collects the **m**etrics, **f**ilters them and
/// **d**eletes the temporary files afterwards.
#[derive(Debug, StructOpt)]
struct Cli {
    /// Path to use for the links to the GitHub repositories. By default, the
    /// file contains links from the `awesome-rust` list.
    #[structopt(
        long = "input_path",
        short = "p",
        default_value = "../data/collector/in/awesome-rust.txt"
    )]
    input_path: String,
    /// Number of repositories to be cloned from the list.
    #[structopt(long = "repo_count", short = "n", default_value = "1")]
    repo_count: usize,
    /// Number of repositories to be skipped on the list.
    #[structopt(long = "repo_skips", short = "s", default_value = "0")]
    repo_skips: usize,
    /// Number of repositories per batch
    #[structopt(long = "batch_size", short = "b", default_value = "16")]
    batch_size: usize,
    /// Option for cloning the repositories into the `tmp` folder. If `-d`
    /// is omitted, this flag only needs to be set once.
    #[structopt(long = "clone_repos", short = "c")]
    clone: bool,
    /// Option to collect metrics. The output of this step can be found in the
    /// `out` directory.
    #[structopt(long = "collect_metrics", short = "m")]
    metrics: bool,
    /// Option to filter the metrics. This reorganizes and filters the raw
    /// outputs from the `out` directory and saves the results in `res`.
    #[structopt(long = "filter_metrics", short = "f")]
    filter: bool,
    /// Option to delete the temporary files immediately after the metrics are
    /// collected and filtered. This can be useful in order to save disk space
    /// when `-n` is large.
    #[structopt(long = "delete_tmp", short = "d")]
    delete: bool,
}
