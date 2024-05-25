#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>

#include "data_collector.h"

#define BUFF_SIZE 4096
#define MAX_LINE_SIZE 1024

static char buffer[BUFF_SIZE] = "";

static int data_file = 0;

static unsigned long long get_timestamp_ms(void)
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000ULL + tv.tv_usec / 1000ULL;
}

static void flush_data()
{
    int ret = 0;
    int data_len = 0;

    if (data_file <= 0)
    {
        printf("Warning! Data file not initialized!\n");
        memset(buffer, 0, sizeof(buffer));
        return;
    }

    data_len = strlen(buffer);
    ret = write(data_file, buffer, data_len);
    if (ret != data_len)
    {
        printf("Error writing data to file!\n");
        raise(SIGTERM);
    }

    memset(buffer, 0, sizeof(buffer));
}

void data_collector_init(const char *filename_prefix)
{
    char filename[100];
    sprintf(filename, "out/%s-%lu.csv", filename_prefix, (long)(get_timestamp_ms() / 1000));

    if (data_file != 0)
    {
        printf("Closing previous data file\n");
        flush_data();
        close(data_file);
    }

    data_file = open(filename, O_CREAT | O_WRONLY, 0744);
    if (data_file <= 0)
    {
        printf("Error opening data file!\n");
        raise(SIGTERM);
    }

    printf("Data collector initialized, output file: '%s'\n", filename);
}

void data_collector_cleanup()
{
    if (data_file > 0)
    {
        printf("Flushing and closing csv file stream\n");
        flush_data();
        data_file = close(data_file);
    }
}

void collect_data(const measurements_wrapper *meas)
{
    char line[MAX_LINE_SIZE] = {0};

    // timestamp_ms, ambient_light, confidence_zi_t0, distance_zi_t0, confidence_zi_t1, distance_zi_t1 
    sprintf(line, "%llu", meas->timestamp_ms);
    sprintf(line + strlen(line), ",%d", meas->ambient_light);
    for (int i = 0; i < 9; i++) {
        sprintf(line + strlen(line), ",%d,%d", meas->confidences[2 * i], meas->distances[2 * i]);
        sprintf(line + strlen(line), ",%d,%d", meas->confidences[2 * i + 1], meas->distances[2 * i + 1]);
    }
    strcat(line, "\n");

    if (strlen(buffer) + (strlen(line) + 1) > BUFF_SIZE)
    {
        flush_data();
    }

    strcat(buffer, line);
}
