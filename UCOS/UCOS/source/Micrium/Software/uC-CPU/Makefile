CFLAGS = -std=c99 -D__WIN32__ -g -DNO_TYPEDEF_OS_FLAGS  
CC = gcc

#调试用目录设置
#BUILD_DIR=/d/learn/UCOS-III-x86-win32/build

CFLAGS += -I$(CURDIR) -I$(CURDIR)/Win32/Visual_Studio -I../../../Microsoft/Windows/Kernel \
          -I../../../Micrium/Software/uC-LIB

SOURCES_C=$(wildcard *.c) 
OBJECTS_C=$(patsubst %.c, $(BUILD_DIR)/uc-cpu/%.obj, $(SOURCES_C))


CPU_C_C=Win32/Visual_Studio/cpu_c.c 
CPU_C_O=$(BUILD_DIR)/uc-cpu/cpu_c.o

BSP_CPU_C=../../../Microsoft/BSP/Windows/bsp_cpu.c
BSP_CPU_O=$(BUILD_DIR)/uc-cpu/bsp_cpu.o

.PHONY: all uc-cpu clean always

all: uc-cpu

uc-cpu: $(BUILD_DIR)/uc-cpu.a

$(BUILD_DIR)/uc-cpu.a: $(OBJECTS_C) $(CPU_C_O) $(BSP_CPU_O)
	$(AR) -rcs $@ $^
	@echo "--> Created  uc-cpu.a"

$(OBJECTS_C): $(SOURCES_C)
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) -c -o $@ $<
	@echo "--> Compiled: " $<

#win32 port
$(CPU_C_O): $(CPU_C_C)
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) -c -o $@ $<
	@echo "--> Compiled: " $<

$(BSP_CPU_O): $(BSP_CPU_C)
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) -c -o $@ $<
	@echo "--> Compiled: " $<


clean:
	@rm -f $(BUILD_DIR)/uc-cpu.a
	@rm -f $(BUILD_DIR)/uc-cpu/*