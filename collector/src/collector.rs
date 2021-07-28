use futures::StreamExt;
use indicatif::ProgressBar;
use log::{error, info};
use std::error::Error;
use url::Url;

use crate::repo::Repo;

/// Enum containing all pipeline tasks
pub enum CollectorTask {
    CloneRepos,
    CollectMetrics,
    FilterMetrics,
    DeleteTmp,
}

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
            error!("Could not parse url {}: {}", url_str, url.unwrap_err());
            return;
        }

        let url = url.unwrap();
        let repo = Repo::new(&url);
        let path = url.path();

        match task {
            CollectorTask::CloneRepos => {
                info!("Cloning {}", path);
                repo.clone().await;
            }
            CollectorTask::CollectMetrics => {
                info!("Collecting metrics on {}", path);
                repo.metrics().await;
            }
            CollectorTask::FilterMetrics => {
                info!("Filtering metrics on {}", path);
                repo.filter().await;
            }
            CollectorTask::DeleteTmp => {
                info!("Deleting tmp of {}", path);
                repo.delete();
            }
        }

        progress_bar.inc(1);
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
