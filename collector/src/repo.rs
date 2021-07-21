use crate::utils::findings_to_json;
use crate::{
    out::OutFile,
    src::SrcFile,
    tool::ToolName,
    utils::{get_data_path, snip_path},
};
use async_gitlib::RepoClone;
use futures::StreamExt;
use std::{
    fs,
    path::{Path, PathBuf},
};
use url::Url;

pub struct Repo<'a> {
    pub url: &'a Url,
    pub tmp_path: PathBuf,
}

impl<'a> Repo<'a> {
    pub fn new(url: &'a Url) -> Self {
        let tmp_path = Self::get_path(url, None, "tmp");
        Self { url, tmp_path }
    }

    pub fn get_path(url: &Url, tool_name: Option<&ToolName>, folder: &str) -> PathBuf {
        let repo_name = url.path().strip_prefix("/").unwrap();
        let mut out_path = get_data_path();

        out_path.push(folder);

        if let Some(tool_name) = tool_name {
            out_path.push(tool_name.to_string());
        }

        out_path.push(repo_name);
        out_path
    }

    pub fn get_src_files(&self) -> Vec<SrcFile> {
        let mut src_files = Vec::new();

        let tmp_path = Path::new(&self.tmp_path);
        let rust_file_paths = crate::utils::get_rust_files(tmp_path);

        for rust_file_path in rust_file_paths {
            let mut out_files: Vec<OutFile> = Vec::new();

            for tool in crate::tool::all_tools() {
                let mut out_path = Repo::get_path(&self.url, Some(&tool.name), "out");
                let out_path_end: PathBuf = snip_path(&rust_file_path, 3);

                let mut out_file_name = match tool.name {
                    ToolName::Clippy => tool.name.to_string(),
                    _ => out_path_end.to_str().unwrap().replace("/", "_"),
                };
                out_file_name.push_str(".json");

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

    pub async fn clone(&self) {
        let mut task = RepoClone::default();

        if task.clone(self.url.as_str(), &self.tmp_path).await.is_err() {
            task.set_branch("main");
            task.clone(self.url.as_str(), &self.tmp_path)
                .await
                .unwrap_or_else(|err| {
                    eprintln!(
                        "Skipped {}: {}",
                        self.tmp_path.to_str().unwrap(),
                        err.message()
                    );
                });
        }
    }

    pub async fn metrics(&self) {
        let tools = crate::tool::all_tools();
        let size = tools.len();

        let tool_jobs = futures::stream::iter(tools.into_iter().map(|mut tool| async move {
            tool.run(self).await.unwrap_or_else(|err| {
                eprintln!("Failed to run tool {} on {}: {}", tool.name, self.url, err);
            });
        }))
        .buffer_unordered(size)
        .collect::<Vec<()>>();

        tool_jobs.await;
    }

    pub async fn filter(&self) {
        let res_path = Self::get_path(&self.url, None, "res");

        for src_file in self.get_src_files() {
            let findings = src_file.get_findings();
            let root = findings_to_json(findings);

            src_file.save_findings(&res_path, root);
        }
    }

    pub fn delete(&self) {
        let mut tmp_path = PathBuf::from(&self.tmp_path);
        tmp_path.pop();

        let tmp_path = tmp_path.to_str().unwrap();

        fs::remove_dir_all(&tmp_path).unwrap_or_else(|err| {
            eprintln!("Failed to delete tmp folder {}: {}", tmp_path, err);
        });
    }
}
