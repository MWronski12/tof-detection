#ifndef MEASUREMENTS_H
#define MEASUREMENTS_H

#include <inttypes.h>
#include <stdbool.h>

struct measurements_wrapper
{
    unsigned long long timestamp_ms;
    int ambient_light;
    int confidences[18];
    int distances[18];
} typedef measurements_wrapper;

void measurements_init();
void measurements_cleanup();
bool get_measurements(measurements_wrapper *out);

#endif // MEASUREMENTS_H
