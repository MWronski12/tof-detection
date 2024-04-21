#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <signal.h>
#include <stdarg.h>
#include <sys/time.h>

#include "measurements.h"

#include "linux/i2c/ams/tmf882x.h"

/* -------------------------------------------------------------------------- */
/*                                    Init                                    */
/* -------------------------------------------------------------------------- */

static int IS_INITIALIZED = 0;

static int idev = 0;
static int cdev = 0;

void measurements_cleanup(int signal)
{
    printf("Received signal %d. Cleaning up\n", signal);
    close(idev);
    close(cdev);
    exit(EXIT_FAILURE);
}

static void register_measurements_cleanup_handlers(int n_signals, ...)
{
    va_list args;
    va_start(args, n_signals);

    for (int i = 0; i < n_signals; i++)
    {
        int sig = va_arg(args, int);
        if (signal(sig, measurements_cleanup) == SIG_ERR)
        {
            perror("Failed to register signal handler!\n");
            exit(EXIT_FAILURE);
        }
    }
}

void measurements_init()
{
    printf("================ INIT_START ================\n");
    printf("Registering measurements_cleanup handlers\n");
    register_measurements_cleanup_handlers(2, SIGINT, SIGTERM);

    printf("Initializing sensor\n");
    system("./preset.sh");

    printf("Writing calibration data 'calib.bin'\n");
    int calib = open("calib.bin", O_RDONLY);
    if (calib <= 0)
    {
        printf("Error opening calibration data file!\n");
        exit(EXIT_FAILURE);
    }

    char buff[1024];
    int calib_data_len = read(calib, buff, sizeof(buff));
    if (calib_data_len <= 0)
    {
        perror("Failed to read calib.bin!\n");
        close(calib);
        exit(EXIT_FAILURE);
    }

    int calibration_data = open("sysfs/app/calibration_data", O_WRONLY);
    if (calibration_data <= 0)
    {
        perror("Error opening sysfs/app/calibration_data\n");
        close(calib);
        exit(EXIT_FAILURE);
    }

    int ret = write(calibration_data, buff, calib_data_len);
    if (ret != calib_data_len)
    {
        perror("Error writing calibration data!\n");
        close(calib);
        close(calibration_data);
        exit(EXIT_FAILURE);
    }

    close(calibration_data);
    close(calib);

    idev = open("input", O_RDONLY);
    if (idev <= 0)
    {
        perror("Failed to open input device!\n");
        exit(EXIT_FAILURE);
    }
    printf("Input dev opened!\n");

    cdev = open("device", O_RDONLY);
    if (cdev <= 0)
    {
        printf("Failed to open device!\n");
        close(idev);
        exit(EXIT_FAILURE);
    }
    printf("Char dev opened!\n");

    IS_INITIALIZED = 1;
    printf("=============== INIT_COMPLETE ==============\n");
}

/* -------------------------------------------------------------------------- */
/*                                 DATA SOURCE                                */
/* -------------------------------------------------------------------------- */

#define NUM_CHANNELS 9

static int handle_tmf882x_msg_meas_results(struct tmf882x_msg_meas_results *res)
{
    int acc_dist = 0;
    int result_count = 0;

    for (size_t i = 0; i < res->num_results; i++)
    {
        struct tmf882x_meas_result *result = &res->results[i];
        if (result->channel != 5)
            continue;
        acc_dist += result->distance_mm;
        result_count++;
    }

    return result_count > 0 ? acc_dist / result_count : 0;
}

int32_t measurements_get_distance()
{
    if (!IS_INITIALIZED)
    {
        printf("Cannot perform single measurement, device not initialized!\n");
        return -1;
    }

    static char buf[TMF882X_MAX_MSG_SIZE];
    size_t off = 0;
    ssize_t ret = 0;

    ret = read(cdev, buf, sizeof(buf));
    if (ret <= 0)
    {
        perror("Failed to read from device\n");
        measurements_cleanup(SIGTERM);
        exit(EXIT_FAILURE);
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
            return -1;

        case ID_MEAS_RESULTS:
            res = (struct tmf882x_msg_meas_results *)(&msg->meas_result_msg);
            int dist_mm = handle_tmf882x_msg_meas_results(res);
            return (int32_t)dist_mm;

        default:
            printf("Unexpected message id: %d\n", msg->hdr.msg_id);
            return -1;
        }

        off += msg->hdr.msg_len;
    }

    return -1;
}

/* -------------------------------------------------------------------------- */
/*                                    MAIN                                    */
/* -------------------------------------------------------------------------- */

void print_result(int dist_mm)
{
    printf("Result: %d mm\n", dist_mm);
}

int _main()
{
    measurements_init();

    int N_MEASUREMENTS = 10;
    struct timeval start, end;

    gettimeofday(&start, NULL);
    for (int i = 0; i < N_MEASUREMENTS; i++)
    {
        int32_t dist = measurements_get_distance(print_result);
        if (dist == -1)
        {
            printf("Failed to execute single read!\n");
        }

        printf("Distance: %d", dist);
    }
    gettimeofday(&end, NULL);

    printf("================= RESULTS =================\n");

    double seconds = (end.tv_sec - start.tv_sec);
    long micros = ((seconds * 1000000) + end.tv_usec) - (start.tv_usec);
    // double exec_time = micros / N_MEASUREMENTS;

    printf("Num measurements: %d\n", N_MEASUREMENTS);
    printf("Avg measurement time: %f ms\n", micros / (float)N_MEASUREMENTS / 1000.0);

    printf("=================== END ===================\n");
    measurements_cleanup(SIGTERM);
    exit(EXIT_SUCCESS);
}
