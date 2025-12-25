CFLAGS = -std=c99 -D__WIN32__ -g -DNO_TYPEDEF_OS_FLAGS  
CC = gcc

#调试用目录设置
#BUILD_DIR=/d/learn/UCOS-III-x86-win32/build

CFLAGS += -I../Ports/Win32/Visual_Studio \
          -I../../../../Microsoft/Windows/Kernel \
          -I../../../../Microsoft/Windows/Kernel/OS3 \
		  -I../../uC-CPU -I../../uC-CPU/Win32/Visual_Studio \
		  -I../../uC-LIB 
    

SOURCES_C=$(wildcard *.c) 
OBJECTS_C=$(patsubst %.c, $(BUILD_DIR)/uc-os/%.o, $(SOURCES_C))

AR_OBJS= os_cfg_app.o os_core.o os_dbg.o os_flag.o \
         os_mem.o os_mon.o os_msg.o os_mutex.o os_prio.o os_q.o \
		  os_sem.o os_stat.o os_task.o os_tick.o os_time.o os_tmr.o os_var.o 

OS_CPU_C_C=../Ports/Win32/Visual_Studio/os_cpu_c.c
OS_CPU_C_O=$(BUILD_DIR)/uc-os/os_cpu_c.o

.PHONY: all uc-os clean always

all: uc-os

uc-os: $(BUILD_DIR)/uc-os.a

$(BUILD_DIR)/uc-os.a: $(OBJECTS_C) $(AR_OBJS)  $(OS_CPU_C_O)
	$(AR) -rcs $@ $^
	@echo "--> Created  uc-os.a"

$(OBJECTS_C): $(SOURCES_C)
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) -c -o $@ $<
	@echo "--> Compiled: " $<

$(OS_CPU_C_O): $(OS_CPU_C_C)
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) -c -o $@ $<
	@echo "--> Compiled: " $<

	
clean:
	@rm -f $(BUILD_DIR)/uc-os.a
	@rm -f $(BUILD_DIR)/uc-os/*