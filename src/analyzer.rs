use futures::StreamExt;
use std::error::Error;
use url::Url;

use crate::{repo::Repo, Cli};

#[tokio::main]
pub(crate) async fn analyze(repos: Vec<&str>, args: &Cli) -> Result<(), Box<dyn Error>> {
    let repo_jobs = futures::stream::iter(repos.into_iter().map(|url_str| async move {
        let url = Url::parse(url_str);

        if url.is_err() {
            eprintln!("Could not parse url {}: {}", url_str, url.unwrap_err());
            return;
        }

        let url = url.unwrap();
        let repo = Repo::new(&url);

        if args.clone {
            println!("Cloning {}", repo.url);
            repo.clone().await;
        }
        if args.metrics {
            println!("Collecting metrics on {}", repo.url);
            repo.metrics().await;
        }
        if args.filter {
            println!("Filtering metrics on {}", repo.url);
            repo.filter().await;
        }
        if args.delete {
            println!("Deleting tmp of {}", repo.url);
            repo.delete();
        }
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
