
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
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

int main()
{
    printf("Registering cleanup handlers\n");
    register_cleanup_handlers(2, SIGINT, SIGTERM);

    int server_fd;
    int new_socket;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket failed");
        raise(SIGTERM);
    }

    fflush(stdout);

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET,
                   SO_REUSEADDR | SO_REUSEPORT, &opt,
                   sizeof(opt)))
    {
        perror("setsockopt");
        raise(SIGTERM);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address,
             sizeof(address)) < 0)
    {
        perror("bind failed");
        raise(SIGTERM);
    }

    if (listen(server_fd, 3) < 0)
    {
        perror("listen");
        raise(SIGTERM);
    }

    printf("Listening for connections\n");

    while (1)
    {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                                 &addrlen)) < 0)
        {
            perror("accept");
            raise(SIGTERM);
        }

        printf("Client connected!\n");

        measurements_init();
        data_collector_init();

        while (1)
        {
            int distance = measurements_get_distance();
            collect_data(distance);

            if (distance == -1)
            {
                perror("Measurement failed!");
                raise(SIGTERM);
            }

            int32_t network_data = htonl(distance);
            int ret = send(new_socket, &network_data, sizeof(network_data), MSG_NOSIGNAL);

            if (ret != sizeof(network_data))
            {
                printf("Client closed connection...\n");
                break;
            }
        }

        cleanup();

        // closing the connected socket
        close(new_socket);
    }

    // closing the listening socket
    printf("Shutting down server\n");

    close(server_fd);
    cleanup();

    return 0;
}
