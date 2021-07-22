use serde_json::Value;
use std::path::PathBuf;

use crate::{
    finding::Finding,
    tool::ToolName,
    utils::{self, snip_path},
};

/// This struct represents a single output file generated by a `Tool` which is
/// saved in the `out` folder. It contains the JSON value, the path and the
/// tool it was created with.
pub struct OutFile {
    pub path: PathBuf,
    value: Value,
    tool_name: ToolName,
}

impl OutFile {
    /// Creates a new `OutFile`.
    pub fn new(path: PathBuf, tool_name: ToolName) -> Self {
        let value = utils::read_json(&path).unwrap_or_default();

        Self {
            path,
            value,
            tool_name,
        }
    }

    /// Reads the contents of the output file and extracts a list of `Findings`.
    pub fn extract_findings(&self, src_file_path: PathBuf) -> Vec<Finding> {
        let empty = Vec::new();
        let entries = self.value.as_array().unwrap_or(&empty);
        let mut findings = Vec::new();

        match self.tool_name {
            ToolName::Rca | ToolName::Node => {
                let spaces = utils::get_spaces(&self.value);

                for space in spaces {
                    let finding = Finding::new(
                        self.tool_name,
                        space["kind"].as_str().unwrap().to_string(),
                        space["name"].as_str().unwrap().to_string(),
                        space["start_line"].as_u64().unwrap(),
                        space["end_line"].as_u64().unwrap(),
                        Some(&space["metrics"]),
                    );

                    findings.push(finding);
                }
            }
            ToolName::Finder => {
                for entry in entries {
                    let finding = Finding::new(
                        self.tool_name,
                        entry["kind"].as_u64().unwrap().to_string(),
                        entry["name"].as_str().unwrap().to_string(),
                        entry["start_line"].as_u64().unwrap(),
                        entry["end_line"].as_u64().unwrap(),
                        None,
                    );

                    findings.push(finding);
                }
            }
            ToolName::Clippy => {
                for entry in entries {
                    if entry["reason"].as_str().unwrap() != "compiler-message" {
                        continue;
                    }

                    let name = entry["message"]["code"]["code"].as_str();
                    let kind = entry["message"]["level"].as_str().unwrap_or_default();

                    if name.is_none() {
                        continue;
                    }

                    let entry_src_path = entry["target"]["src_path"].as_str().unwrap();
                    let entry_src_path: PathBuf = snip_path(&entry_src_path, 1);

                    if !src_file_path.ends_with(&entry_src_path) {
                        continue;
                    }

                    let name = name.unwrap();
                    let prefix = format!("{}::", self.tool_name.to_string());
                    let name = match name.starts_with(&prefix) {
                        true => name.strip_prefix(&prefix).unwrap(),
                        false => continue,
                    };

                    let start_line = entry["message"]["spans"][0]["line_start"].as_u64().unwrap();
                    let end_line = entry["message"]["spans"][0]["line_end"].as_u64().unwrap();

                    if entry["message"]["spans"].as_array().into_iter().len() > 1 {
                        eprintln!("More than one span for a clippy message");
                    }

                    let finding = Finding::new(
                        self.tool_name,
                        kind.to_string(),
                        name.to_string(),
                        start_line,
                        end_line,
                        None,
                    );

                    findings.push(finding);
                }
            }
        };

        findings
    }
}
