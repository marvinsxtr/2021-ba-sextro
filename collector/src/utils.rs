use log::error;
use serde::Serialize;
use serde_json::{json, Map, Value};
use std::{
    env,
    error::Error,
    ffi::OsStr,
    fs::{self, File},
    io::{BufReader, ErrorKind},
    path::{Path, PathBuf},
};
use walkdir::WalkDir;

use crate::finding::Finding;

/// Reads a JSON file and returns the respective value.
pub fn read_json<P: AsRef<Path>>(path: P) -> Result<Value, Box<dyn Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let v: Value = serde_json::from_reader(reader)?;

    Ok(v)
}

/// Saves a JSON value to a file at the given path.
pub fn save_json<S: Serialize>(data: &S, path: &Path, output_path: &Path) -> std::io::Result<()> {
    let format_ext = ".json";

    let path = path.strip_prefix("/").unwrap_or(path);
    let path = path.strip_prefix("./").unwrap_or(path);

    let cleaned_path: Vec<&str> = path
        .iter()
        .map(|os_str| {
            let s_str = os_str.to_str().unwrap();
            if s_str == ".." {
                "_"
            } else {
                s_str
            }
        })
        .collect();

    let filename = cleaned_path.join("_") + format_ext;

    let format_path = output_path.join(filename);

    fs::create_dir_all(output_path).unwrap_or_else(|err| {
        error!(
            "Could not create output folders {}: {}",
            output_path.to_str().unwrap(),
            err
        );
    });

    let format_file = File::create(format_path)?;

    serde_json::to_writer_pretty(format_file, &data)
        .map_err(|e| std::io::Error::new(ErrorKind::Other, e.to_string()))
}

/// Recursively collects a list of paths to Rust files contained in a directory.
pub fn get_rust_files(path: &Path) -> Vec<String> {
    WalkDir::new(path)
        .follow_links(false)
        .into_iter()
        .filter(|e| {
            let e = e.as_ref();

            if e.is_err() {
                return false;
            }

            let e = e.unwrap();
            let file_name = e.file_name().to_string_lossy();
            let path = e.path().to_str().unwrap();

            file_name.ends_with(".rs") && !path.contains("/target/")
        })
        .map(|e| e.unwrap().path().to_owned())
        .map(|e| e.to_string_lossy().to_string())
        .collect()
}

/// Traverses the nested output JSON and returns a list of spaces generated by
/// the `rust-code-analysis` tool.
pub fn get_spaces(value: &Value) -> Vec<&Map<String, Value>> {
    let mut result = Vec::new();
    let mut spaces = Vec::new();

    let first_space = value.as_object();

    if let Some(first_space) = first_space {
        spaces.push(first_space);
    }

    while !spaces.is_empty() {
        let space = spaces.pop().unwrap();

        result.push(space);

        let new_spaces = space["spaces"].as_array().unwrap();

        for new_space in new_spaces {
            let new_space = new_space.as_object().unwrap();
            spaces.push(new_space);
        }
    }

    result
}

/// Trims a path after the `tmp` directory.
pub fn snip_path<S>(path: &S, skips: usize) -> PathBuf
where
    S: AsRef<OsStr>,
{
    Path::new(&path)
        .iter()
        .skip_while(|s| *s != "tmp")
        .skip(skips)
        .collect()
}

/// Returns the `DATA_PATH` environment variable. This is used as the base path
/// for the output files.
pub fn get_data_path() -> PathBuf {
    let default_path = PathBuf::from("../data/collector/");

    match env::var("DATA_PATH") {
        Ok(val) => {
            if val.is_empty() {
                default_path
            } else {
                PathBuf::from(val)
            }
        }
        Err(_) => default_path,
    }
}

/// Returns a JSON value mapping each tool to the list of `Finding`s.
pub fn findings_to_json(findings: Vec<Finding>) -> Value {
    let mut root = json!({});

    for tool in crate::tool::all_tools() {
        root[tool.name.to_string()] = json!([]);
    }

    for finding in findings {
        root.as_object_mut().unwrap()[&finding.tool_name.to_string()]
            .as_array_mut()
            .unwrap()
            .push(json!(finding));
    }

    root
}

/// Initializes the logger to save logs in the `log` folder
pub fn setup_logger() -> Result<(), fern::InitError> {
    let path = get_data_path().join("log");

    fs::create_dir_all(&path).unwrap_or_else(|err| {
        eprintln!("Failed to create logging folder: {}", err);
    });

    fern::Dispatch::new()
        .format(|out, message, record| {
            out.finish(format_args!(
                "{}[{}][{}] {}",
                chrono::Local::now().format("[%Y-%m-%d][%H:%M:%S]"),
                record.target(),
                record.level(),
                message
            ))
        })
        .level(log::LevelFilter::Debug)
        .chain(fern::log_file(path.join(format!(
            "{}.log",
            chrono::Local::now().format("%Y-%m-%d@%H:%M:%S")
        )))?)
        .apply()?;
    Ok(())
}
