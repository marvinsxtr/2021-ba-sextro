use futures::StreamExt;
use std::error::Error;
use url::Url;

use crate::{repo::Repo, Cli};

#[tokio::main]
pub(crate) async fn analyze(repos: Vec<&str>, args: &Cli) -> Result<(), Box<dyn Error>> {
    let repo_jobs = futures::stream::iter(repos.into_iter().map(|url| async move {
        let url = Url::parse(url).unwrap_or_else(|err| {
            eprintln!("Could not parse url {}: {}", url, err);
            panic!();
        });

        let repo = Repo::new(&url);

        if args.analyze_only {
            repo.analyze().await;
        } else {
            repo.clone().await;
            repo.metrics().await;
            repo.analyze().await;

            if args.delete_tmp {
                repo.delete();
            }
        }
    }))
    .buffer_unordered(8)
    .collect::<Vec<()>>();

    repo_jobs.await;

    Ok(())
}
