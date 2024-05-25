#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/time.h>

#include "measurements.h"

#include "linux/i2c/ams/tmf882x.h"

/* -------------------------------------------------------------------------- */
/*                                    Init                                    */
/* -------------------------------------------------------------------------- */

static int IS_INITIALIZED = 0;

static int idev = 0;
static int cdev = 0;

void measurements_cleanup()
{
    if (idev > 0)
    {
        printf("Closing input device\n");
        idev = close(idev);
    }
    if (cdev > 0)
    {
        printf("Closing tmf882x char device\n");
        cdev = close(cdev);
    }
}

void measurements_init()
{
    printf("================ MEASUREMENTS_INIT_START ================\n");
    printf("Measurements size: %d\n", sizeof(measurements_wrapper));

    printf("Initializing sensor\n");
    system("./preset.sh");

    printf("Writing calibration data 'calib.bin'\n");
    int calib = open("calib.bin", O_RDONLY);
    if (calib <= 0)
    {
        printf("Error opening calibration data file!\n");
        raise(SIGTERM);
    }

    char buff[1024];
    int calib_data_len = read(calib, buff, sizeof(buff));
    if (calib_data_len <= 0)
    {
        perror("Failed to read calib.bin!\n");
        close(calib);
        raise(SIGTERM);
    }

    int calibration_data = open("sysfs/app/calibration_data", O_WRONLY);
    if (calibration_data <= 0)
    {
        perror("Error opening sysfs/app/calibration_data\n");
        close(calib);
        raise(SIGTERM);
    }

    int ret = write(calibration_data, buff, calib_data_len);
    if (ret != calib_data_len)
    {
        perror("Error writing calibration data!\n");
        close(calib);
        close(calibration_data);
        raise(SIGTERM);
    }

    close(calibration_data);
    close(calib);

    idev = open("input", O_RDONLY);
    if (idev <= 0)
    {
        perror("Failed to open input device!\n");
        raise(SIGTERM);
    }
    printf("Input dev opened!\n");

    cdev = open("device", O_RDONLY);
    if (cdev <= 0)
    {
        printf("Failed to open device!\n");
        close(idev);
        raise(SIGTERM);
    }
    printf("Char dev opened!\n");

    IS_INITIALIZED = 1;
    printf("=============== MEASUREMENTS_INIT_COMPLETE ==============\n");
}

/* -------------------------------------------------------------------------- */
/*                                 DATA SOURCE                                */
/* -------------------------------------------------------------------------- */

#define NUM_CHANNELS 9

static void print_tmf882x_msg_meas_results(struct tmf882x_msg_meas_results *res)
{
    printf("=============== Results ===================\n");
    printf("ambient_light: %d\n", res->ambient_light);
    printf("num_results: %d\n", res->num_results);
    printf("valid_results: %d\n", res->valid_results);
    printf("photon_count: %d\n", res->photon_count);
    printf("ref_photon_count: %d\n", res->ref_photon_count);
    printf("temperature: %d\n", res->temperature);
    for (size_t i = 0; i < res->num_results; i++)
    {
        struct tmf882x_meas_result *result = &res->results[i];
        // if (result->channel != 5)
        //     continue;
        printf("===================\n");
        printf("ch_target_idx: %d\n", result->ch_target_idx);
        printf("channel: %d\n", result->channel);
        printf("confidence: %d\n", result->confidence);
        printf("distance_mm: %d\n", result->distance_mm);
        printf("sub_capture: %d\n", result->sub_capture);
        printf("===================\n");
    }
}

static unsigned long long get_timestamp_ms(void)
{
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000ULL + tv.tv_usec / 1000ULL;
}

static void handle_tmf882x_msg_meas_results(struct tmf882x_msg_meas_results *res, measurements_wrapper *out)
{
    #define DEBUG__ true
    if (DEBUG__) print_tmf882x_msg_meas_results(res);

    out->timestamp_ms = get_timestamp_ms();
    out->ambient_light = res->ambient_light;
    for (int i = 0; i < 18; i++) {
        out->confidences[i] = -1;
        out->distances[i] = -1;
    }

    for (size_t i = 0; i < res->num_results; i++) {
        struct tmf882x_meas_result *result = &res->results[i];
        out->confidences[2 * (result->channel - 1) + result->ch_target_idx] = result->confidence;
        out->distances[2 * (result->channel - 1) + result->ch_target_idx] = result->distance_mm;
    }
}

bool get_measurements(measurements_wrapper *out)
{
    if (!IS_INITIALIZED)
    {
        printf("Cannot perform single measurement, device not initialized!\n");
        return false;
    }

    static char buf[TMF882X_MAX_MSG_SIZE];
    size_t off = 0;
    ssize_t ret = 0;

    ret = read(cdev, buf, sizeof(buf));
    if (ret <= 0)
    {
        perror("Failed to read from device\n");
        measurements_cleanup(SIGTERM);
        raise(SIGTERM);
    }

    while (off < ret)
    {
        struct tmf882x_msg *msg = (struct tmf882x_msg *)(buf + off);

        struct tmf882x_msg_error *err = NULL;
        struct tmf882x_msg_meas_results *res = NULL;

        switch (msg->hdr.msg_id)
        {
        case ID_ERROR:
            err = (struct tmf882x_msg_error *)(&msg->err_msg);
            printf("Error code %d\n", err->err_code);
            raise(SIGTERM);

        case ID_MEAS_RESULTS:
            res = (struct tmf882x_msg_meas_results *)(&msg->meas_result_msg);
            handle_tmf882x_msg_meas_results(res, out);
            return true;

        default:
            printf("Unexpected message id: %d\n", msg->hdr.msg_id);
            raise(SIGTERM);
        }

        off += msg->hdr.msg_len;
    }

    return -1;
}
