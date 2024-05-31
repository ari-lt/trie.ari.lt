#include <libtrie/gen.h>
#include <libtrie/rng.h>
#include <libtrie/trie.h>
#include <libtrie/null.h>

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int main(const int argc, const char *const argv[]) {
    Trie *t;
    TrieRNG rng;
    FILE *fp;

    long min_size;
    long count;
    long idx;

    uint8_t *s;

    if (argc < 5) {
        fprintf(stderr, "Usage: %s <model.bin> <seed> <min size> <count>\n",
                argv[0]);
        return 1;
    }

    fp = fopen(argv[1], "rb");

    if (!fp) {
        perror("Failed to open the model");
        return 1;
    }

    t = trie_load_file(fp);
    fclose(fp);

    if (!t) {
        fputs("Failed to load tree\n", stderr);
        return 1;
    }

    rng_seed(&rng, (const uint8_t *)argv[2], strlen(argv[2]));

    min_size = atol(argv[3]);

    if (min_size < 1) {
        fputs("Invalid max size\n", stderr);
        return 1;
    }

    count = atol(argv[4]);

    if (count < 1) {
        fputs("Invalid sentence count\n", stderr);
        return 1;
    }

    for (idx = 0; idx < count; ++idx) {
        rng_iter(rng.state, count, idx);
        s = gen_trie_random(t, &rng, (uint64_t)min_size, NULL);
        printf("%s ", s);
        free(s);
    }

    putchar('\n');

    trie_free(t);

    return 0;
}
