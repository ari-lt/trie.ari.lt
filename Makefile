CC := gcc
LIBS := -ltrie

ifeq ($(NOQA),)
  CFLAGS += -std=c89 -ansi -Wall -Wextra -Wpedantic -pedantic -Wshadow -Werror -Wconversion -Wformat -Wuninitialized -Wmissing-prototypes -Wmissing-declarations -Wstrict-prototypes -Wredundant-decls -Wfloat-equal -Wcast-qual -Wnested-externs -Wvla -Winline -Wmissing-format-attribute -Wmissing-noreturn -pedantic-errors
endif

SRC_DIR := cli
BIN_DIR := bin

PREFIX ?= /usr/local
BINDIR := $(PREFIX)/bin

SOURCES := $(wildcard $(SRC_DIR)/*.c)

TARGETS := $(SOURCES:$(SRC_DIR)/%.c=$(BIN_DIR)/%)

all: $(TARGETS)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/%: $(SRC_DIR)/%.c | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LIBS)

install: all
	@echo "Installing binaries to $(BINDIR)"
	@mkdir -p $(BINDIR)
	@cp $(TARGETS) $(BINDIR)

clean:
	rm -rf $(BIN_DIR)

.PHONY: all clean install
