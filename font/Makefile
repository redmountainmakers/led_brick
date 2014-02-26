CROSS := 
CC := $(CROSS)gcc
CXX := $(CROSS)g++
CPP := $(CROSS)cpp
LD := $(CROSS)gcc
CFLAGS += -g -O2 -Wall
CXXFLAGS := $(CFLAGS) -std=c++11
CPPFLAGS := -std=c++11
LDFLAGS := -lopencv_core -lopencv_highgui

CONVERT_OBJS := convert.o

OBJS := $(CONVERT_OBJS)

all: convert
convert: $(CONVERT_OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)
clean:
	rm -f convert $(OBJS)
	rm -rf .deps

%.o: %.cpp Makefile
	-@mkdir -p .deps
	@$(CXX) $(CPPFLAGS) -M -MF .deps/$*.P $<
	$(CXX) $(CXXFLAGS) -c -o $@ $<

-include .deps/$(OBJS:%.o=%.P)
