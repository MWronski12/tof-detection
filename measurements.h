#ifndef MEASUREMENTS_H
#define MEASUREMENTS_H

#include <inttypes.h>
#include <stdbool.h>

struct measurements_wrapper
{
    int num_zones;
    int *distance_mm;
} typedef measurements_wrapper;

void measurements_init();
void measurements_cleanup();
bool get_measurements(measurements_wrapper *out);

#endif // MEASUREMENTS_H