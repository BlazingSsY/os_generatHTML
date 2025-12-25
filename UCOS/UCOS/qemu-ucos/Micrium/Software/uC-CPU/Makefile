# Makefile for a "uC-CPU"  on qemu -M ppce500

# The gnu toolchain is assumed to be in your path.
# Modify $(QEMU) to where your qemu is located

PROC=powerpc
TYPE=linux-gnu
PREFIX=$(PROC)-$(TYPE)-
#PATH:=/usr/local/bin:$(PATH)

#---------------------------------------------------
# TARGET配置
#---------------------------------------------------
# 

#CPU        = MPC57xx-VLE
#BSP        = MPC574XG-324DS
#BSP_SHORT  = MPC574XG
#APP        = Blinky
#LINK_SCRIPT = 57xx_flash.ld

#CPU       = MPC5646C
#BSP       = MPC5646C-UCOS
#BSP_SHORT = MPC5646C
#APP       = mdmc
#CACHE	   = powerpc_e200z4d
#LINK_SCRIPT = MPC5646C_FLASH.ld


#---------------------------------------------------
# QEMU-PPCE500 (MPC8544-DS)
#---------------------------------------------------
# 
CPU       = MPC8544
BSP       = MPC8544-QEMU
BSP_SHORT = MPC8544
APP       = mdmc
CACHE	   = powerpc_e500v2
LINK_SCRIPT = MPC8544_FLASH.ld

#
#---------------------------------------------------
#目录结构常量
#---------------------------------------------------
CPU_CACHE_C_DIR=./Cache/NXP/$(CACHE)
CPU_CACHE_S_DIR=./Cache/NXP/$(CACHE)/GNU
CPU_GNU_S_DIR=./$(CPU)/GNU
CPU_OS_PORT_DIR=../uCOS-III/Ports/PowerPC/$(CPU)/GNU

CPU_CFG_DIR=../../../DMC/$(BSP)/$(APP)


#---------------------------------------------------
#编译配置
#---------------------------------------------------
CFLAGS=-I. \
	   -I$(CPU_GNU_S_DIR) \
	   -I$(CPU_CFG_DIR)\
	   -I../uC-LIB  


CC=$(PREFIX)gcc
AS=$(PREFIX)as
AR=$(PREFIX)ar
LD=$(PREFIX)ld
NM=$(PREFIX)nm
OBJDUMP=$(PREFIX)objdump
OBJCOPY=$(PREFIX)objcopy

QEMU=qemu-system-ppc

CFLAGS += -std=c99 -g -DNO_TYPEDEF_OS_FLAGS  
#---------------------------------------------------
# 调试用目录设置
#---------------------------------------------------
#
BUILD_DIR= ../../../build
#---------------------------------------------------
#目标uc-cpu.a静态库
#---------------------------------------------------
# 
UCPU_LIB = $(BUILD_DIR)/uc-cpu.a

#当前目录uC-CPU下的源文件
SOURCES_C=$(wildcard *.c) 
OBJECTS_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_C:.c=.o)))

#Cache目录下的C源文件
SRC_CPU_CACHE_C=$(wildcard $(CPU_CACHE_C_DIR)/*.c) 
OBJ_CPU_CACHE_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SRC_CPU_CACHE_C:.c=.o)))

#Cache目录下与gnu编译有关的S汇编源文件,被C文件调用
SRC_CPU_CACHE_S=$(wildcard $(CPU_CACHE_S_DIR)/*.S) 
OBJ_CPU_CACHE_S=$(addprefix $(BUILD_DIR)/, $(notdir $(SRC_CPU_CACHE_S:.S=.o)))

#CPU与gnu编译有关的S汇编源文件
SRC_CPU_GNU_S=$(wildcard $(CPU_GNU_S_DIR)/*.S) 
OBJ_CPU_GNU_S=$(addprefix $(BUILD_DIR)/, $(notdir $(SRC_CPU_GNU_S:.S=.o)))


.PHONY: all ucpu clean always
all : ucpu

#---------------------------------------------------
#编译cpu库uc-cpu.a
#---------------------------------------------------
ucpu:$(UCPU_LIB)
$(UCPU_LIB): $(OBJECTS_C)  $(OBJ_CPU_CACHE_C) $(OBJ_CPU_CACHE_S) $(OBJ_CPU_GNU_S)
	$(AR) -rcs $@ $^


# 编译每个.c文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o: %.c
	$(CC) $(CFLAGS) -c -g $< -o $@ 

$(BUILD_DIR)/%.o: $(CPU_CACHE_C_DIR)/%.c 
	$(CC) $(CFLAGS) -c -g $^ -o $@ 

# 编译每个.S文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(OBJ_CPU_CACHE_S) : $(CPU_CACHE_S_DIR)/*.S
	$(CC)  -mregnames -c -g $< -o $@ 

$(OBJ_CPU_GNU_S):  $(CPU_GNU_S_DIR)/*.S
	$(CC)  -mregnames -c -g $< -o $@ 

clean:
	@rm -f $(UCPU_LIB)
	@rm -f $(OBJECTS_C) 
	@rm -f $(OBJ_CPU_CACHE_C) 
	@rm -f $(OBJ_CPU_CACHE_S) 
	@rm -f $(OBJ_CPU_GNU_S) 


