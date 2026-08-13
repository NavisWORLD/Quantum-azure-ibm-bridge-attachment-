#ifndef QBT_H
#define QBT_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) && defined(QBT_FFI_IMPORT)
#define QBT_API __declspec(dllimport)
#else
#define QBT_API
#endif

/* Static protocol version string. Do not free. */
QBT_API const char *qbt_version(void);

/* Returns owned JSON. Release with qbt_free_string. */
QBT_API char *qbt_simulator_packet(uint64_t seed, uint64_t shots);

/*
 * request_json is a NUL-terminated JSON object containing at least `counts`.
 * Returns owned QuantumState JSON or {"error": ...}.
 */
QBT_API char *qbt_normalize_counts_json(const char *request_json);

/* Releases owned strings returned by QBT FFI. */
QBT_API void qbt_free_string(char *value);

#ifdef __cplusplus
}
#endif

#endif /* QBT_H */
