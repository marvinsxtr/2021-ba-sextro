use serde::Serialize;
use serde_json::{Map, Value};
use std::{error::Error, ffi::OsStr, fs::{self, File}, io::{BufReader, ErrorKind}, path::{Path, PathBuf}};
use walkdir::WalkDir;

pub fn read_json_from_file<P: AsRef<Path>>(path: P) -> Result<Value, Box<dyn Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let v: Value = serde_json::from_reader(reader)?;

    Ok(v)
}

pub fn get_rust_files(path: &Path) -> Vec<String> {
    WalkDir::new(path)
        .follow_links(false)
        .into_iter()
        .filter(|e| {
            let e = e.as_ref().unwrap();
            let file_name = e.file_name().to_string_lossy();
            let path = e.path().to_str().unwrap();

            file_name.ends_with(".rs") && !path.contains("/target/")
        })
        .map(|e| e.unwrap().path().to_owned())
        .map(|e| e.to_string_lossy().to_string())
        .collect()
}

pub fn get_spaces(value: &Value) -> Vec<&Map<String, Value>> {
    let mut result = Vec::new();
    let mut spaces = Vec::new();

    let first_space = value.as_object().unwrap();

    spaces.push(first_space);

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

pub fn snip_path<S>(path: &S, skips: usize) -> PathBuf where S: AsRef<OsStr> {
    Path::new(&path)
        .iter()
        .skip_while(|s| *s != "tmp")
        .skip(skips)
        .collect()
}

pub fn dump_findings<S: Serialize>(
    data: &S,
    path: &Path,
    output_path: &PathBuf,
) -> std::io::Result<()> {
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
        eprintln!(
            "Could not create output folders {}: {}",
            output_path.to_str().unwrap(),
            err
        );
    });

    let format_file = File::create(format_path)?;

    serde_json::to_writer_pretty(format_file, &data)
        .map_err(|e| std::io::Error::new(ErrorKind::Other, e.to_string()))
}
