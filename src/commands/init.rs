use colored::Colorize;
use std::fs;

pub fn execute() {
    println!("{}", "[ INIT ] Initializing Flint-X project...".yellow().bold());

    let config = r#"{
  "version": "0.1.0",
  "project": "flintx-project",
  "ai_endpoint": "http://localhost:8000/analyze",
  "ollama_model": "mistral",
  "output_dir": "./flintx_output"
}
"#;

    fs::create_dir_all("flintx_output").expect("Failed to create output directory");
    fs::write("flintx.config.json", config).expect("Failed to write config file");

    println!("{}", "  ✔ Created flintx.config.json".green());
    println!("{}", "  ✔ Created flintx_output/ directory".green());
    println!();
    println!("{}", "  Flint-X project ready.".bold());
    println!("  Edit {} to configure your AI endpoint and model.", "flintx.config.json".cyan());
}