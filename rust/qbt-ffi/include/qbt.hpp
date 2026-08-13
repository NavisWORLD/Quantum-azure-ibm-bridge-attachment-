#ifndef QBT_HPP
#define QBT_HPP

#include "qbt.h"

#include <cstdint>
#include <stdexcept>
#include <string>

namespace qbt {

inline std::string version() {
    const char *value = qbt_version();
    return value ? std::string(value) : std::string();
}

inline std::string take_owned(char *value) {
    if (!value) {
        throw std::runtime_error("QBT returned a null pointer");
    }
    std::string result(value);
    qbt_free_string(value);
    return result;
}

inline std::string simulator_packet(std::uint64_t seed, std::uint64_t shots) {
    return take_owned(qbt_simulator_packet(seed, shots));
}

inline std::string normalize_counts_json(const std::string &request_json) {
    return take_owned(qbt_normalize_counts_json(request_json.c_str()));
}

}  // namespace qbt

#endif  // QBT_HPP
