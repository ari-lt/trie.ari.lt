#include <libtrie/trie.h>

#include <stdio.h>

#define BUF_SIZE 16384

int main(const int argc, const char *const argv[]) {
    Trie *t;
    FILE *fp;
    int c;
    uint64_t idx;
    uint8_t buf[BUF_SIZE] = {0};

    if (argc < 2) {
        fprintf(stderr, "Usage: echo ... | %s <model.bin>\n", argv[0]);
        return 1;
    }

    fp = fopen(argv[1], "rb");

    if (fp) {
        puts("Loading the old model...");

        t = trie_load_file(fp);
        fclose(fp);

        if (!t) {
            fputs("Failed to load tree\n", stderr);
            return 1;
        }
    } else {
        puts("Creating a new model...");

        t = trie_create_node('\0');

        if (!t) {
            fputs("Failed to create tree\n", stderr);
            return 1;
        }
    }

    puts("Updating the model...");

    idx = 0;

    while ((c = getchar()) != EOF) {
        buf[idx++] = c == '\n' || c == '\r' ? ' ' : (uint8_t)c;

        if (idx >= (BUF_SIZE - 2) || c == '.' || c == '?' || c == '!') {
            buf[idx] = '\0';
            trie_insert_sentence(t, buf);
            idx = 0;
        }
    }

    puts("Saving the model...");

    fp = fopen(argv[1], "wb");

    if (!fp) {
        fputs("Failed to open the model file.\n", stderr);
        trie_free(t);
        return 1;
    }

    trie_save_file(fp, t);

    puts("Freeing resources...");

    fclose(fp);
    trie_free(t);

    return 0;
}
