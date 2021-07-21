use futures::StreamExt;
use std::error::Error;
use url::Url;

use crate::{repo::Repo, Cli};

#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
pub(crate) async fn collect(repos: Vec<&str>, args: &Cli) -> Result<(), Box<dyn Error>> {
    let repo_jobs = futures::stream::iter(repos.into_iter().map(|url_str| async move {
        let url = Url::parse(url_str);

        if url.is_err() {
            eprintln!("Could not parse url {}: {}", url_str, url.unwrap_err());
            return;
        }

        let url = url.unwrap();
        let repo = Repo::new(&url);
        let path = url.path();

        if args.clone {
            println!("Cloning {}", path);
            repo.clone().await;
        }
        if args.metrics {
            println!("Collecting metrics on {}", path);
            repo.metrics().await;
        }
        if args.filter {
            println!("Filtering metrics on {}", path);
            repo.filter().await;
        }
        if args.delete {
            println!("Deleting tmp of {}", path);
            repo.delete();
        }
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
