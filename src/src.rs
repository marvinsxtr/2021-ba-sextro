use std::{collections::HashMap, path::PathBuf};

use crate::{finding::Finding, metrics::Metrics, out::OutFile, tool::ToolName, utils::{dump_findings, snip_path}};

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

    pub fn save_findings(&self, res_path: &PathBuf, findings: Vec<Finding>) {
        let res_file_path: PathBuf = snip_path(&self.path, 3);
        dump_findings(&findings, &res_file_path, &res_path.to_path_buf()).unwrap_or_default();
    }

    pub fn analyze_out_files(
        &'a mut self,
        mappings: &'a mut HashMap<&'static str, Metrics>,
    ) -> &'a HashMap<&str, Metrics> {
        let findings = self.get_findings();

        println!("File: {:?}", self.path);

        for finding in &findings {
            if finding.tool_name == ToolName::Finder {
                for other_finding in &findings {
                    if finding.is_inside(other_finding) && other_finding.tool_name == ToolName::Rca
                    {
                        let size_ratio = finding.get_size_ratio(other_finding);
                        if size_ratio <= 0.1 {
                            continue;
                        }

                        match finding.identifier.as_str() {
                            "lifetime" => {
                                *mappings.entry("lifetime").or_default() +=
                                    other_finding.get_metrics().unwrap().weigh(size_ratio)
                            }
                            "trait_bounds" => {
                                *mappings.entry("trait_bounds").or_default() +=
                                    other_finding.get_metrics().unwrap().weigh(size_ratio)
                            }
                            "reference_type" => {
                                *mappings.entry("reference_type").or_default() +=
                                    other_finding.get_metrics().unwrap().weigh(size_ratio)
                            }
                            "macro_invocation" => {
                                *mappings.entry("macro_invocation").or_default() +=
                                    other_finding.get_metrics().unwrap().weigh(size_ratio)
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
