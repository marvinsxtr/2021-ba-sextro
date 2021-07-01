use serde_json::Value;
use std::path::{Path, PathBuf};

use crate::{finding::Finding, tool::ToolName, utils};

pub struct OutFile {
    pub path: PathBuf,
    value: Value,
    tool_name: ToolName,
}

impl OutFile {
    pub fn new(path: PathBuf, tool_name: ToolName) -> Self {
        let value = utils::read_json_from_file(&path).unwrap_or_default();

        Self {
            path,
            value,
            tool_name,
        }
    }

    pub fn extract_findings(&self, src_file_path: PathBuf) -> Vec<Finding> {
        let empty = Vec::new();
        let entries = self.value.as_array().unwrap_or(&empty);
        let mut findings = Vec::new();

        match self.tool_name {
            ToolName::Rca => {
                let spaces = utils::get_spaces(&self.value);

                for space in spaces {
                    let finding = Finding::new(
                        self.tool_name,
                        space["kind"].as_str().unwrap().to_string(),
                        space["start_line"].as_u64().unwrap(),
                        space["end_line"].as_u64().unwrap(),
                        Some(&space["metrics"]),
                    );

                    findings.push(finding);
                }
            }
            ToolName::Finder => {
                for entry in entries {
                    let start_line = entry["start_position"].as_array().unwrap()[0]
                        .as_u64()
                        .unwrap();
                    let end_line = entry["end_position"].as_array().unwrap()[0]
                        .as_u64()
                        .unwrap();

                    let kind = entry["kind"].as_str().unwrap().to_string();

                    let finding = Finding::new(self.tool_name, kind, start_line, end_line, None);

                    findings.push(finding);
                }
            }
            ToolName::Clippy => {
                for entry in entries {
                    if entry["reason"].as_str().unwrap() != "compiler-message" {
                        continue;
                    }

                    let identifier = entry["message"]["code"]["code"].as_str();

                    if identifier.is_none() {
                        continue;
                    }

                    let entry_src_path = entry["target"]["src_path"].as_str().unwrap();
                    let entry_src_path: PathBuf = Path::new(&entry_src_path)
                        .iter()
                        .skip_while(|s| *s != "tmp")
                        .skip(1)
                        .collect();

                    if !src_file_path.ends_with(&entry_src_path) {
                        continue;
                    }

                    let prefix = format!("{}::", self.tool_name.to_string());

                    let identifier = identifier.unwrap();
                    let identifier = match identifier.starts_with(&prefix) {
                        false => continue,
                        true => identifier.strip_prefix(&prefix).unwrap(),
                    };

                    let start_line = entry["message"]["spans"][0]["line_start"].as_u64().unwrap();
                    let end_line = entry["message"]["spans"][0]["line_end"].as_u64().unwrap();

                    if entry["message"]["spans"].as_array().into_iter().len() > 1 {
                        panic!("More than one span for a clippy message");
                    }

                    let finding = Finding::new(
                        self.tool_name,
                        identifier.to_string(),
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
