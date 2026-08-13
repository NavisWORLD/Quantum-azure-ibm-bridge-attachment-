use qbt_bridge::providers::SimulatorProvider;
use qbt_bridge::QuantumBridge;

#[test]
fn simulator_builds_bounded_packet() {
    let mut bridge = QuantumBridge::new(vec![Box::new(SimulatorProvider::new(7))]);
    let status = bridge.connect();
    assert_eq!(status["simulator"]["active"], true);

    let packet = bridge.control_packet(512);
    assert_eq!(packet.qbt_version, "1.0");
    assert_eq!(packet.active_sources, 1);
    assert!((0.0..=1.0).contains(&packet.quantum_mix));
    assert_eq!(packet.states[0].execution_mode, "simulator");
    assert_eq!(packet.states[0].normalized_vector.len(), 4);
    assert_eq!(packet.states[0].result_digest.len(), 64);
}

#[test]
fn empty_bridge_falls_back() {
    let mut bridge = QuantumBridge::new(vec![]).with_fallback(0.5);
    let packet = bridge.control_packet(128);
    assert_eq!(packet.active_sources, 0);
    assert_eq!(packet.quantum_mix, 0.5);
}
