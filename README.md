# GitHub Rust Tool

Tool to collect usability metrics from GitHub repositories and analyze the results.

# Collector

## Setup

### Install rust-code-analysis-cli

Uninstall any previous version of the CLI

```shell
cargo uninstall rust-code-analysis-cli
```

Clone the forked rust-code-analysis tool

```shell
git clone https://github.com/marvinsxtr/rust-code-analysis.git
```

Install the patched version

```shell
cargo install --path rust-code-analysis/rust-code-analysis-cli
```

### Build the GitHub Rust Tool

```shell
cargo build
cargo build --release
```

## Usage

### Flags

```
-c, --clone_repos        
-d, --delete_tmp         
-f, --filter_metrics     
-m, --collect_metrics    
```

### Options

```
-p, --input_path <input-path>     [default: ../data/in/awesome-rust.txt]
-n, --repo_count <repo-count>     [default: 1]
-s, --repo_skips <repo-skips>     [default: 0]
```

# Analyzer