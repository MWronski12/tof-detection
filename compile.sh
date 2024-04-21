gcc -Werror -Wall -pedantic \
    -I driver/include \
    -o build/main \
    -O0 \
    data_collector.h data_collector.c measurements.c measurements.h main.c
