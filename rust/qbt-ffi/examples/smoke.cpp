#include "qbt.hpp"

#include <iostream>
#include <string>

int main() {
    if (qbt::version() != "1.0") {
        return 1;
    }
    const std::string packet = qbt::simulator_packet(11, 128);
    std::cout << packet << '\n';
    return packet.find("\"active_sources\":1") != std::string::npos ? 0 : 2;
}
