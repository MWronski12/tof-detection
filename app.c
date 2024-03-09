#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>

#include "linux/i2c/ams/tmf882x.h"

#define NUM_CHANNELS 9


void handle_tmf882x_msg_meas_results(struct tmf882x_msg_meas_results *res)
{
    // printf("=====================================\n");
    // printf("Ambient light: %d\n", res->ambient_light);
    // printf("Valid resutls: %d\n", res->valid_results);
    int acc_dist[NUM_CHANNELS] = {0};
    int result_count[NUM_CHANNELS] = {0};
    // printf("result_num: %d\n", res->result_num);
    for (size_t i = 0; i < res->num_results; i++)
    {
        struct tmf882x_meas_result *result = &res->results[i];
        acc_dist[result->channel - 1] += result->distance_mm;
        result_count[result->channel - 1]++;
        // printf("\ndist: %d\n", result->distance_mm);
        // printf("channel: %d\n", result->channel);
        // printf("sub_capture: %d\n", result->sub_capture);
    }
    // printf("=====================================\n");
    FILE *view = fopen("view", "w");
    if (view == NULL)
    {
        printf("Failed to open view file\n");
        return;
    }
    fprintf(view, "%d\t%d\t%d\n %d\t%d\t%d\n %d\t%d\t%d\n",
            result_count[0] > 0 ? acc_dist[0] / result_count[0] : 0,
            result_count[1] > 0 ? acc_dist[1] / result_count[1] : 0,
            result_count[2] > 0 ? acc_dist[2] / result_count[2] : 0,
            result_count[3] > 0 ? acc_dist[3] / result_count[3] : 0,
            result_count[4] > 0 ? acc_dist[4] / result_count[4] : 0,
            result_count[5] > 0 ? acc_dist[5] / result_count[5] : 0,
            result_count[6] > 0 ? acc_dist[6] / result_count[6] : 0,
            result_count[7] > 0 ? acc_dist[7] / result_count[7] : 0,
            result_count[8] > 0 ? acc_dist[8] / result_count[8] : 0);
            // result_count[9] > 0 ? acc_dist[9] / result_count[9] : 0,
    //         result_count[10] > 0 ? acc_dist[10] / result_count[10] : 0,
    //         result_count[11] > 0 ? acc_dist[11] / result_count[11] : 0,
    //         result_count[12] > 0 ? acc_dist[12] / result_count[12] : 0,
    //         result_count[13] > 0 ? acc_dist[13] / result_count[13] : 0,
    //         result_count[14] > 0 ? acc_dist[14] / result_count[14] : 0,
    //         result_count[15] > 0 ? acc_dist[15] / result_count[15] : 0,
    //         result_count[16] > 0 ? acc_dist[16] / result_count[16] : 0,
    //         result_count[17] > 0 ? acc_dist[17] / result_count[17] : 0);

    fclose(view);
}

int main()
{
    int fd = open("device", O_RDONLY);
    if (fd < 0)
    {
        printf("Failed to open device\n");
        return -1;
    }

    char buf[TMF882X_MAX_MSG_SIZE];
    size_t off = 0;
    ssize_t ret = 0;

    while (1)
    {
        ret = read(fd, buf, sizeof(buf));
        if (ret <= 0)
        {
            printf("Failed to read from device\n");
            return -1;
        }

        off = 0;
        while (off < ret)
        {
            struct tmf882x_msg *msg = (struct tmf882x_msg *)(buf + off);

            struct tmf882x_msg_error *err;
            struct tmf882x_msg_meas_results *res;
            struct tmf882x_msg_meas_stats *stats;
            struct tmf882x_msg_histogram *hist;

            switch (msg->hdr.msg_id)
            {
            case ID_ERROR:
                err = (struct tmf882x_msg_error *)(&msg->err_msg);
                printf("Error code %d\n", err->err_code);
                return -1;
            case ID_MEAS_RESULTS:
                res = (struct tmf882x_msg_meas_results *)(&msg->meas_result_msg);
                handle_tmf882x_msg_meas_results(res);
                break;
            case ID_MEAS_STATS:
                stats = (struct tmf882x_msg_meas_stats *)&msg->meas_stat_msg;
                printf("Stats received!\n", err->err_code);
                break;
            case ID_HISTOGRAM:
                hist = (struct tmf882x_msg_histogram *)(&msg->hist_msg);
                printf("Stats received!\n", err->err_code);
                break;
            default:
                printf("Unknown message id: %d\n", msg->hdr.msg_id);
                return -1;
            }

            off += msg->hdr.msg_len;
        }
    }

    close(fd);
    return 0;
}
