
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "measurements.h"

#define PORT 8080

int main()
{
    measurements_init();

    int server_fd;
    int new_socket;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket failed");
        measurements_cleanup(0);
        exit(EXIT_FAILURE);
    }

    fflush(stdout);

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET,
                   SO_REUSEADDR | SO_REUSEPORT, &opt,
                   sizeof(opt)))
    {
        perror("setsockopt");
        measurements_cleanup(0);
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address,
             sizeof(address)) < 0)
    {
        perror("bind failed");
        measurements_cleanup(0);
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0)
    {
        perror("listen");
        measurements_cleanup(0);
        exit(EXIT_FAILURE);
    }

    printf("Listening for connections\n");

    while (1)
    {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                                 &addrlen)) < 0)
        {
            perror("accept");
            measurements_cleanup(0);
            exit(EXIT_FAILURE);
        }

        printf("Client connected!\n");

        while (1)
        {
            int distance = measurements_get_distance();
            if (distance == -1)
            {
                perror("Measurement failed!");
                measurements_cleanup(0);
                exit(EXIT_FAILURE);
            }

            int32_t network_data = htonl(distance);
            int ret = send(new_socket, &network_data, sizeof(network_data), MSG_NOSIGNAL);

            if (ret != sizeof(network_data))
            {
                printf("Client closed connection...\n");
                break;
            }
        }

        // closing the connected socket
        close(new_socket);
    }

    // closing the listening socket
    printf("Shutting down server\n");

    close(server_fd);
    measurements_cleanup(0);

    return 0;
}
