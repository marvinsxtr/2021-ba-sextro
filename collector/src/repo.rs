use crate::utils::findings_to_json;
use crate::{
    out::OutFile,
    src::SrcFile,
    tool::ToolName,
    utils::{get_data_path, snip_path},
};
use async_gitlib::RepoClone;
use futures::StreamExt;
use log::{error, info, warn};
use std::{
    fs,
    path::{Path, PathBuf},
};
use url::Url;
use walkdir::WalkDir;

/// This struct represents a repository. It contains a url and a temporary path.
pub struct Repo<'a> {
    pub url: &'a Url,
    pub tmp_path: PathBuf,
    pub out_path: PathBuf,
    pub res_path: PathBuf,
}

impl<'a> Repo<'a> {
    /// Creates a new `Repo`.
    pub fn new(url: &'a Url) -> Self {
        let tmp_path = Self::get_path(url, None, "tmp");
        let out_path = Self::get_path(url, None, "out");
        let res_path = Self::get_path(url, None, "res");

        Self {
            url,
            tmp_path,
            out_path,
            res_path,
        }
    }

    /// Utility function for getting the tool- or repository-specific paths
    /// inside the directory specified by the `DATA_PATH` environment variable.
    pub fn get_path(url: &Url, tool_name: Option<&ToolName>, folder: &str) -> PathBuf {
        let repo_name = url.path().strip_prefix("/").unwrap();
        let mut out_path = get_data_path();

        out_path.push(folder);
        out_path.push(repo_name);

        if let Some(tool_name) = tool_name {
            out_path.push(tool_name.to_string());
        }

        out_path
    }

    /// Returns a list of `SrcFile`s which are associated to this repository.
    pub fn get_src_files(&self) -> Vec<SrcFile> {
        let mut src_files = Vec::new();

        let tmp_path = Path::new(&self.tmp_path);
        let rust_file_paths = crate::utils::get_rust_files(tmp_path);

        for rust_file_path in rust_file_paths {
            let mut out_files: Vec<OutFile> = Vec::new();

            for tool in crate::tool::all_tools() {
                let out_path_end: PathBuf = snip_path(&rust_file_path, 3);

                let mut out_file_name = match tool.name {
                    ToolName::Clippy => tool.name.to_string(),
                    _ => out_path_end.to_str().unwrap().replace("/", "_"),
                };
                out_file_name.push_str(".json");

                let mut out_path = self.out_path.clone();

                out_path.push(tool.name.to_string());
                out_path.push(out_file_name);

                let out_file = OutFile::new(out_path.to_path_buf(), tool.name);
                out_files.push(out_file);
            }

            let src_path = PathBuf::from(&rust_file_path);
            let src_file = SrcFile::new(src_path, out_files);

            src_files.push(src_file);
        }

        src_files
    }

    /// Clones the repository into the `tmp` folder via https.
    pub async fn clone(&self) {
        if Path::new(&self.tmp_path).exists() {
            info!(
                "Skipped cloning {}: Folder already exists",
                &self.url.path()
            );
            return;
        }

        let mut task = RepoClone::default();

        if task.clone(self.url.as_str(), &self.tmp_path).await.is_err() {
            task.set_branch("main");
            task.clone(self.url.as_str(), &self.tmp_path)
                .await
                .unwrap_or_else(|err| {
                    warn!(
                        "Skipped {}: {}",
                        self.tmp_path.to_str().unwrap(),
                        err.message()
                    );
                });
        }
    }

    /// Collects metrics on the repository by running all tools on it. The
    /// output is saved in the `out` directory.
    pub async fn metrics(&self) {
        if Path::new(&self.out_path).exists() {
            info!(
                "Skipped collecting metrics on {}: Folder already exists",
                &self.url.path()
            );
            return;
        }

        let tools = crate::tool::all_tools();
        let size = tools.len();

        let tool_jobs = futures::stream::iter(tools.into_iter().map(|mut tool| async move {
            tool.run(self).await.unwrap_or_else(|err| {
                error!("Failed to run tool {} on {}: {}", tool.name, self.url, err);
            });
        }))
        .buffer_unordered(size)
        .collect::<Vec<()>>();

        tool_jobs.await;
    }

    /// Filters and reorganizes the raw output files by collecting and saving a
    /// uniform list of `Finding`s.
    pub async fn filter(&self) {
        if Path::new(&self.res_path).exists() {
            info!(
                "Skipped filtering metrics on {}: Folder already exists",
                &self.url.path()
            );
            return;
        }

        for src_file in self.get_src_files() {
            let findings = src_file.get_findings();
            let root = findings_to_json(findings);

            src_file.save_findings(&self.res_path, root);
        }
    }

    /// Deletes the cloned repository from the `tmp` directory.
    pub fn delete(&self) {
        if !Path::new(&self.tmp_path).exists() {
            info!(
                "Skipped deleting {}: Folder does not exist",
                &self.url.path()
            );
            return;
        }

        fs::remove_dir_all(&self.tmp_path).unwrap_or_else(|err| {
            error!(
                "Could not delete {}: {}",
                self.tmp_path.to_str().unwrap(),
                err
            );
        });

        let mut tmp_path = self.tmp_path.clone();
        tmp_path.pop();

        let remaining = WalkDir::new(tmp_path.clone()).into_iter().count();
        if remaining == 1 {
            fs::remove_dir(tmp_path.clone()).unwrap_or_else(|err| {
                error!("Could not delete {}: {}", tmp_path.to_str().unwrap(), err)
            });
        }
    }
}
