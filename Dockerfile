# The legacy server stores pointers in 32-bit integers; retain its i386 ABI.
FROM i386/debian:bookworm AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libmariadb-dev-compat zlib1g-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY saac/ saac/
COPY gmsv/ gmsv/
RUN make -C saac clean && make -C gmsv clean && \
    make -C saac -j4 CC='gcc -fcommon -fgnu89-inline' CFLAGS='-O1 -g -I. -I./include' && \
    make -C gmsv -j4 CFLAGS='-O1 -g -fcommon -fgnu89-inline -I. -I.. -I./include -I../include'

FROM i386/debian:bookworm AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 zlib1g python3 && rm -rf /var/lib/apt/lists/*
COPY --from=build /src/saac/saacjt.exe /opt/stoneage/saac
COPY --from=build /src/gmsv/gmsvjt.exe /opt/stoneage/gmsv
COPY gmsv/data/ /opt/stoneage/world/data/
COPY gmsv/setup.cf gmsv/log.cf /opt/stoneage/world/
COPY saac/data/ /opt/stoneage/account-data/
COPY docker/entrypoint.py docker/healthcheck.py /opt/stoneage/
ENTRYPOINT ["python3", "/opt/stoneage/entrypoint.py"]
CMD ["gmsv"]

FROM build AS test
COPY tests/ tests/
RUN gcc -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -fcommon -fgnu89-inline -ffunction-sections -fdata-sections \
    -I./saac/include -Wl,--gc-sections tests/saac_read_buffer.c -o /tmp/buffer-test && \
    ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 timeout 30 /tmp/buffer-test

# Keep plain `docker build` producing the runtime, not the test toolchain.
FROM runtime AS final
