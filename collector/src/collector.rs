use futures::StreamExt;
use std::error::Error;
use url::Url;

use crate::{repo::Repo, CollectorTask};

/// Runs a pipeline task on a batch of repositories
#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
pub(crate) async fn run_on_batch(
    repos: Vec<&str>,
    task: &CollectorTask,
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

        match task {
            CollectorTask::CloneRepos => {
                println!("Cloning {}", path);
                repo.clone().await;
            }
            CollectorTask::CollectMetrics => {
                println!("Collecting metrics on {}", path);
                repo.metrics().await;
            }
            CollectorTask::FilterMetrics => {
                println!("Filtering metrics on {}", path);
                repo.filter().await;
            }
            CollectorTask::DeleteTmp => {
                println!("Deleting tmp of {}", path);
                repo.delete();
            }
        }
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
