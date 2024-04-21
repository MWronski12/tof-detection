#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>

#include "data_collector.h"

#define BUFF_SIZE 4096
#define MAX_LINE_SIZE 100

static char buffer[BUFF_SIZE] = "";

static int data_file = 0;

unsigned long long get_timestamp_ms(void)
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000ULL + tv.tv_usec / 1000ULL;
}

static void flush_data()
{
    int ret = 0;
    int data_len = 0;

    if (data_file == 0)
    {
        printf("Warning! Data file not initialized!\n");
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

void data_collector_init()
{
    char filename[50];

    if (data_file != 0)
    {
        printf("Warning! Data file already initialized!\n");
        return;
    }

    sprintf(filename, "out/data-%llu.csv", get_timestamp_ms());

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
    flush_data();
    close(data_file);
}

void collect_data(int32_t distance)
{
    char line[MAX_LINE_SIZE] = {0};
    unsigned long long timestamp = get_timestamp_ms();
    sprintf(line, "%llu,%d\n", timestamp, distance);

    if (strlen(buffer) + (strlen(line) + 1) > BUFF_SIZE)
    {
        flush_data();
    }

    strcat(buffer, line);
}

int data_collector_main()
{
    data_collector_init();
    for (int i = 0; i < 2800; i++)
    {
        collect_data(i);
    }
    data_collector_cleanup();
    return 0;
}
