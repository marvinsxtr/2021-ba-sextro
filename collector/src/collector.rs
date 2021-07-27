use futures::StreamExt;
use indicatif::ProgressBar;
use std::{
    error::Error,
    io::{stdout, Write},
};
use url::Url;

use crate::{repo::Repo, CollectorTask};

/// Runs a pipeline task on a batch of repositories
#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
pub(crate) async fn collect(
    repos: Vec<&str>,
    task: &CollectorTask,
    progress_bar: &ProgressBar,
) -> Result<(), Box<dyn Error>> {
    let repo_jobs = futures::stream::iter(repos.into_iter().map(|url_str| async move {
        let url = Url::parse(url_str);

        if url.is_err() {
            eprintln!("Could not parse url {}: {}", url_str, url.unwrap_err());
            return;
        }

        let url = url.unwrap();
        let repo = Repo::new(&url);
        let path = url.path();

        let mut stdout = stdout();

        match task {
            CollectorTask::CloneRepos => {
                print!("Cloning {}\r", path);
                repo.clone().await;
            }
            CollectorTask::CollectMetrics => {
                print!("Collecting metrics on {}\r", path);
                repo.metrics().await;
            }
            CollectorTask::FilterMetrics => {
                print!("Filtering metrics on {}\r", path);
                repo.filter().await;
            }
            CollectorTask::DeleteTmp => {
                print!("Deleting tmp of {}\r", path);
                repo.delete();
            }
        }

        progress_bar.inc(1);

        stdout.flush().unwrap();
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
