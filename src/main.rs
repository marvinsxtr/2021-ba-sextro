use std::{
    env, io, fs::File, process,
    io::{
        BufRead, BufReader
    },
};

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let config = Config::new(&args).unwrap_or_else(|err| {
        println!("Problem parsing arguments: {}", err);
        process::exit(1);
    });

    println!("Reading {:?} ...", config.path);
    analyze_file(File::open(config.path.as_str())?);

    Ok(())
}

struct Config {
    path: String
}

impl Config {
    fn new(args: &[String]) -> Result<Config, &str> {
        if args.len() < 2 {
            return Err("Not enough arguments");
        }

        let path = args[1].clone();
        Ok(Config { path })
    }
}

fn analyze_file(file: File) {
    let buf_reader = BufReader::new(file);

    let mut rust_commits: i32 = 0;
    let mut all_commits: i32 = 0;

    for line in buf_reader.lines() {
        let line = line.unwrap_or_else(|err| {
            println!("Problem reading line: {}", err);
            process::exit(1);
        });

        if line.to_string().contains(".rs") {
            rust_commits += 1;
        }

        all_commits += 1;
    }

    let percentage: f32 = (rust_commits as f32 / all_commits as f32) * 100.;

    println!("File contains {:?} / {:.2}% commits with rust", rust_commits, percentage);
}
