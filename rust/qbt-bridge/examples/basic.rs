use qbt_bridge::providers::SimulatorProvider;
use qbt_bridge::QuantumBridge;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut bridge = QuantumBridge::new(vec![Box::new(SimulatorProvider::new(7))]);
    println!("{:#?}", bridge.connect());

    let packet = bridge.control_packet(2048);
    println!("{}", serde_json::to_string_pretty(&packet)?);
    Ok(())
}
