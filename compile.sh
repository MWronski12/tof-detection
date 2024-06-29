if [ $# -gt 2 ]; then
    echo "Usage: $0 optional[--headless]"
    exit 1
fi

if [ "$1" = "--headless" ]; then
    echo "Compiling headless version"
    main="headless_main.c"
else
    echo "Compiling server version"
    main="main.c"
fi

gcc -Werror -Wall -pedantic \
    -I driver/include \
    -o build/main \
    -O0 \
    data_collector.h data_collector.c measurements.c measurements.h ${main}
