use std::{collections::HashMap, path::PathBuf};

use crate::{finding::Finding, metrics::Metrics, out::OutFile, tool::ToolName};

pub struct SrcFile {
    path: PathBuf,
    out_files: Vec<OutFile>,
}

impl<'a> SrcFile {
    pub fn new(path: PathBuf, out_files: Vec<OutFile>) -> Self {
        Self { path, out_files }
    }

    pub fn get_findings(&self) -> Vec<Finding> {
        let mut findings: Vec<Finding> = Vec::new();

        for out_file in &self.out_files {
            let path = self.path.to_path_buf();
            let mut new_findings = out_file.extract_findings(path);
            findings.append(&mut new_findings)
        }

        findings
    }

    pub fn analyze_out_files(&'a mut self, mappings: &'a mut HashMap<&'static str, Metrics>) -> &'a HashMap<&str, Metrics> {
        let findings = self.get_findings();
        // println!("File: {:?}", self.path);

        for finding in &findings {
            if finding.tool_name == ToolName::Finder {
                for other_finding in &findings {
                    if finding.intersect(other_finding) && other_finding.tool_name == ToolName::Rca {
                        // println!("{:?}", other_finding.get_metrics().unwrap());

                        match finding.identifier.as_str() {
                            "lifetime" =>  {
                                *mappings.entry("lifetime").or_default() += other_finding.get_metrics().unwrap()
                            },
                            "trait_bounds" => {
                                *mappings.entry("trait_bounds").or_default() += other_finding.get_metrics().unwrap()
                            },
                            "reference_type" => {
                                *mappings.entry("reference_type").or_default() += other_finding.get_metrics().unwrap()
                            },
                            "macro_invocation" => {
                                *mappings.entry("macro_invocation").or_default() += other_finding.get_metrics().unwrap()
                            }
                            &_ => {}
                        }
                    }
                }
            }
        }
        mappings
    }
}