#ifndef DATA_COLLECTOR_H
#define DATA_COLLECTOR_H

#include <stdint.h>

#include "measurements.h"

void data_collector_init();
void data_collector_cleanup();
void collect_data(const measurements_wrapper *meas);

#endif // DATA_COLLECTOR_H
