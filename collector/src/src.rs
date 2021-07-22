use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::{
    finding::Finding,
    out::OutFile,
    utils::{save_json, snip_path},
};

/// This struct represents one source file in a repository. It contains a path
/// and a list of `OutFiles`.
pub struct SrcFile {
    path: PathBuf,
    out_files: Vec<OutFile>,
}

impl<'a> SrcFile {
    /// Creates a new `SrcFile`.
    pub fn new(path: PathBuf, out_files: Vec<OutFile>) -> Self {
        Self { path, out_files }
    }

    /// Iterates over all output files and collects a list of `Finding`s.
    pub fn get_findings(&self) -> Vec<Finding> {
        let mut findings: Vec<Finding> = Vec::new();

        for out_file in &self.out_files {
            let path = self.path.to_path_buf();
            let mut new_findings = out_file.extract_findings(path);
            findings.append(&mut new_findings)
        }

        findings
    }

    /// Saves the findings as a JSON file at a given path.
    pub fn save_findings(&self, res_path: &Path, findings: Value) {
        let res_file_path: PathBuf = snip_path(&self.path, 3);
        save_json(&findings, &res_file_path, &res_path.to_path_buf()).unwrap_or_default();
    }
}
