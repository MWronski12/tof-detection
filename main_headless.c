
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

#include "data_collector.h"
#include "measurements.h"

#define PORT 8080

static void cleanup()
{
    measurements_cleanup();
    data_collector_cleanup();
}

static void cleanup_handler(int signal)
{
    printf("Received signal %d, cleaning up...\n", signal);
    cleanup();
    exit(EXIT_FAILURE);
}

static void register_cleanup_handlers(int n_signals, ...)
{
    va_list args;
    va_start(args, n_signals);

    for (int i = 0; i < n_signals; i++)
    {
        int sig = va_arg(args, int);
        if (signal(sig, cleanup_handler) == SIG_ERR)
        {
            perror("Failed to register signal handler!\n");
            exit(EXIT_FAILURE);
        }
    }
}

int main(int argc, char **argv)
{
    char filename_prefix[100] = "data";
    if (argc == 2)
    {
        strcpy(filename_prefix, argv[1]);
    }

    printf("Registering cleanup handlers\n");
    register_cleanup_handlers(2, SIGINT, SIGTERM);

    measurements_init();
    data_collector_init(filename_prefix);

    while (1)
    {
        measurements_wrapper meas;
        bool meas_ok = get_measurements(&meas);
        if (!meas_ok)
        {
            printf("Error reading measurements\n");
            raise(SIGTERM);
        }

        collect_data(&meas);
    }

    cleanup();

    return 0;
}
