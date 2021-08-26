# GitHub Rust Tool

Tool to collect usability metrics from GitHub repositories and analyze the results.

### Data path

For both collector and analyzer, the variable `DATA_PATH` can be changed to an absolute path, where any result may be saved.

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

### Build and run

```
cd collector
```

#### Debug

```shell
cargo build
./target/debug/collector
```

#### Release

```shell
cargo build --release
./target/release/collector
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

## Documentation

```
cargo doc
```

Open `target/doc/collector/index.html` in a browser.

## Logs

The logs can be found in the `log` directory under the `DATA_PATH`.

# Analyzer

## Setup

### Virtual environment

```sh
cd analyzer
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```sh
pip3 install -r requirements.txt
```

## Run

```
cd ..
python3 -m analyzer
```

## Scripts

```
python3 -m analyzer.scripts.<SCRIPT>
```

## Usage

### Options

```
-n REPO_COUNT, --repo_count REPO_COUNT - Number of repositories to analyze
-s SKIP_REPOS, --skip_repos SKIP_REPOS - Number of repositories to skip
-a, --analyze_repos - Whether to analyze the repositories
-t, --statistic_tests - Whether to conduct the statistical tests
-e EXPERIMENT_NAMES, --experiment_names EXPERIMENT_NAMES - Which experiments to run
```