use async_gitlib::RepoClone;
use std::{
    collections::HashMap,
    fs,
    path::{Path, PathBuf},
};
use url::Url;

use crate::{metrics::Metrics, out::OutFile, src::SrcFile, tool::ToolName, utils::snip_path};

pub struct Repo<'a> {
    pub url: &'a Url,
    pub tmp_path: PathBuf,
}

impl<'a> Repo<'a> {
    pub fn new(url: &'a Url) -> Self {
        let tmp_path = Self::get_tmp_path(url);
        Self { url, tmp_path }
    }

    pub fn get_tmp_path(url: &Url) -> PathBuf {
        let repo_name = url.path().strip_prefix("/").unwrap();
        let mut tmp_path = PathBuf::from("./data/tmp");

        tmp_path.push(repo_name);
        tmp_path
    }

    pub fn get_path(&self, tool_name: Option<&ToolName>, folder: &str) -> PathBuf {
        let repo_name = self.url.path().strip_prefix("/").unwrap();
        let mut out_path = PathBuf::from(format!("./data/{}", folder));

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
                let mut out_path = self.get_path(Some(&tool.name), "out");
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
        for mut tool in crate::tool::all_tools() {
            tool.run(self).await.unwrap_or_else(|err| {
                eprintln!("Failed to run tool {} on {}: {}", tool.name, self.url, err);
            });
        }
    }

    pub async fn filter(&self) {
        for src_file in self.get_src_files() {
            let findings = src_file.get_findings();
            let res_path = &self.get_path(None, "res");

            src_file.save_findings(res_path, findings);
        }
    }

    pub async fn analyze(&self) {
        let mut mapping: HashMap<&str, Metrics> = HashMap::new();

        for mut src_file in self.get_src_files() {
            src_file.analyze_out_files(&mut mapping);
        }

        for (identifier, metrics) in mapping {
            println!("{}: {:#?}", identifier, metrics.avg())
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
