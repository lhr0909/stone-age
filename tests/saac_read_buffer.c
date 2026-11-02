/* Exercise the actual private buffer reader which crashed on the GS handshake. */
#define main saac_program_main
#include "../saac/main.c"
#undef main
#include <assert.h>

static void reset(const char *text) {
    memset(mb, 0, 2 * sizeof(*mb));
    memset(con, 0, sizeof(*con));
    mbsize = 2; mbuse = 1;
    con[0].use = 1; con[0].mbtop_ri = 0;
    mb[0].use = 1; mb[0].next = -1;
    mb[0].len = strlen(text);
    memcpy(mb[0].buf, text, mb[0].len);
}
int main(void) {
    char out[16] = {0};
    mb = calloc(2, sizeof(*mb)); con = calloc(1, sizeof(*con));
    reset(""); con[0].mbtop_ri = -1;
    assert(getLineReadBuffer(0, out, sizeof(out)) == 0);
    reset("partial");
    assert(getLineReadBuffer(0, out, sizeof(out)) == 0);
    reset("ok\r\n");
    assert(tcpstruct_readline_chop(0, out, sizeof(out)) == 2);
    assert(strcmp(out, "ok") == 0);
    reset("\n");
    assert(tcpstruct_readline_chop(0, out, sizeof(out)) == 0);
    reset("four\n");
    assert(tcpstruct_readline_chop(0, out, 4) == TCPSTRUCT_ETOOLONG);
    free(mb); free(con);
    puts("saac buffer regression checks passed");
    return 0;
}
