#include "qbt.h"

#include <stdio.h>
#include <string.h>

int main(void) {
    const char *version = qbt_version();
    if (version == NULL || strcmp(version, "1.0") != 0) {
        return 1;
    }

    char *packet = qbt_simulator_packet(7, 128);
    if (packet == NULL) {
        return 2;
    }
    int ok = strstr(packet, "\"active_sources\":1") != NULL;
    puts(packet);
    qbt_free_string(packet);
    return ok ? 0 : 3;
}
