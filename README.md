# GitHub Rust Tool

Tool to extract usability metrics from GitHub repositories and analyze the results.

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
cargo install -p rust-code-analysis/rust-code-analysis-cli
```

### Build the GitHub Rust Tool

```shell
cargo build
```

## Usage

### Options

```
-p, --input_path <input-path>     [default: ./data/in/awesome-rust.txt]
-c, --repo_count <repo-count>     [default: 1]
```