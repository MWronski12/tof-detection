
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 8080

int main()
{
    int server_fd;
    int new_socket;
    ssize_t valread;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);

    char buffer[1024] = {0};

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    printf("I am created...\n");
    fflush(stdout);

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET,
                   SO_REUSEADDR | SO_REUSEPORT, &opt,
                   sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    printf("I am set...\n");
    fflush(stdout);

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address,
             sizeof(address)) < 0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    printf("I am bound...\n");
    fflush(stdout);

    if (listen(server_fd, 3) < 0)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("I am listening for connections...\n");
    fflush(stdout);

    while (1)
    {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                                 &addrlen)) < 0)
        {
            perror("accept");
            exit(EXIT_FAILURE);
        }

        printf("I am accepted...\n");
        fflush(stdout);

        while (1)
        {
            char msg[] = "Hello World!";
            int ret = send(new_socket, msg, sizeof(msg) - 1, MSG_NOSIGNAL); // Exclude null terminator
            if (ret != sizeof(msg) - 1)
            {
                printf("Client closed connection or error occurred...\n");
                break;
            }
            sleep(1); // Delay before sending next message
        }

        // closing the connected socket
        close(new_socket);
        printf("I have closed conn socket!\n");
    }

    // closing the listening socket
    close(server_fd);
    printf("I have closed myself!\n");

    return 0;
}
