use std::collections::BTreeMap;
use std::io::{self, Write};
use std::path::PathBuf;

use clap::{Parser, Subcommand, ValueEnum};
use qbt_bridge::providers::{IbmQuantumProvider, SimulatorProvider};
use qbt_bridge::{
    config_status, load_env_file, write_env_file, QbtError, QuantumBridge, Result, CONFIG_KEYS,
};

#[derive(Debug, Parser)]
#[command(name = "qbt-rs", version, about = "Quantum Bridge Transformer Rust CLI")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    Doctor,
    Configure {
        #[arg(long, default_value = ".env")]
        file: PathBuf,
    },
    Status {
        #[arg(long, value_enum, default_value_t = ProviderArg::Simulator)]
        provider: ProviderArg,
    },
    Sample {
        #[arg(long, value_enum, default_value_t = ProviderArg::Simulator)]
        provider: ProviderArg,
        #[arg(long, default_value_t = 1024)]
        shots: u64,
        #[arg(long, default_value_t = 42)]
        seed: u64,
    },
}

#[derive(Debug, Clone, Copy, ValueEnum, Default)]
enum ProviderArg {
    #[default]
    Simulator,
    Ibm,
}

fn bridge_for(provider: ProviderArg, seed: u64) -> QuantumBridge {
    match provider {
        ProviderArg::Simulator => QuantumBridge::new(vec![Box::new(SimulatorProvider::new(seed))]),
        ProviderArg::Ibm => QuantumBridge::new(vec![Box::new(IbmQuantumProvider::from_env())]),
    }
}

fn configure(file: PathBuf) -> Result<()> {
    println!("QBT Rust configuration. Leave any field blank to skip it.");
    println!("Secrets are written only to the local file you choose; .env is gitignored.");

    let mut values = BTreeMap::new();
    for key in CONFIG_KEYS {
        print!("{key}: ");
        io::stdout().flush()?;
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        let value = input.trim();
        if !value.is_empty() {
            values.insert((*key).to_string(), value.to_string());
        }
    }
    write_env_file(&file, &values)?;
    println!("Wrote {}", file.display());
    Ok(())
}

fn run() -> Result<()> {
    let _ = load_env_file(None, false);
    let cli = Cli::parse();

    match cli.command {
        Command::Doctor => {
            println!("{}", serde_json::to_string_pretty(&config_status())?);
        }
        Command::Configure { file } => configure(file)?,
        Command::Status { provider } => {
            let mut bridge = bridge_for(provider, 42);
            let status = bridge.connect();
            println!("{}", serde_json::to_string_pretty(&status)?);
        }
        Command::Sample {
            provider,
            shots,
            seed,
        } => {
            let mut bridge = bridge_for(provider, seed);
            bridge.connect();
            let packet = bridge.control_packet(shots);
            println!("{}", serde_json::to_string_pretty(&packet)?);
            if packet.active_sources == 0 {
                return Err(QbtError::Provider(
                    "no provider produced a sample; inspect provider_errors".to_string(),
                ));
            }
        }
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("qbt-rs: {error}");
        std::process::exit(1);
    }
}
