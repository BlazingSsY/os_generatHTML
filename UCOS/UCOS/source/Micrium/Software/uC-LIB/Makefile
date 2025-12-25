CFLAGS = -std=c99 -D__WIN32__ -g -DNO_TYPEDEF_OS_FLAGS  
CC = gcc

#调试用目录设置
#BUILD_DIR=/d/learn/UCOS-III-x86-win32/build

CFLAGS += -I$(CURDIR) \
		  -I../../../Microsoft/Windows/Kernel \
          -I../../../Microsoft/Windows/Kernel/OS3 \
		  -I../uC-CPU -I../uC-CPU/Win32/Visual_Studio \
		
    

SOURCES_C=$(wildcard *.c) 
OBJECTS_C=$(patsubst %.c, $(BUILD_DIR)/uc-lib/%.o, $(SOURCES_C))
AR_OBJ=lib_ascii.o lib_math.o lib_mem.o lib_str.o

.PHONY: all uc-os clean always

all: uc-os

uc-os: $(BUILD_DIR)/uc-lib.a

$(BUILD_DIR)/uc-lib.a: $(OBJECTS_C) $(AR_OBJ)
	$(AR) -rcs $@ $^
	@echo "--> Created  uc-lib.a"

$(OBJECTS_C): $(SOURCES_C)
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) -c -o $@ $<
	@echo "--> Compiled: " $<


clean:
	@rm -f $(BUILD_DIR)/uc-lib.a
	@rm -f $(BUILD_DIR)/uc-lib/*