CROSS := 
CC := $(CROSS)gcc
CPP := $(CROSS)cpp
LD := $(CROSS)gcc
CFLAGS += -g -O2 -Wall

CONVERT_OBJS := convert.o

OBJS := $(CONVERT_OBJS)

all: convert
convert: $(CONVERT_OBJS)
clean:
	rm -f convert $(OBJS)
	rm -rf .deps

%.o: %.c Makefile
	-@mkdir -p .deps
	@$(CC) $(CPPFLAGS) -M -MF .deps/$*.P $<
	$(CC) $(CFLAGS) -c -o $@ $<

-include .deps/$(OBJS:%.o=%.P)
