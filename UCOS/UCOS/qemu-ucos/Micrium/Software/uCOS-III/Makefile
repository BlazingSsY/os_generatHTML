# Makefile for a "uCOS-III"  on qemu -M ppce500

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


#---------------------------------------------------
# 编译INCLUDE目录
#---------------------------------------------------
# 
UCPU_PORT_DIR=../uC-CPU/$(CPU)/GNU
UCOS_PORT_DIR=./Ports/PowerPC/$(CPU)/GNU
APP_PORT_DIR=../../../DMC/$(BSP)/$(APP)
UCOS_SRC_DIR=./Source


CFLAGS=-I. \
	   -I../uC-LIB \
	   -I../uC-CPU \
	   -I./Source \
	   -I$(UCPU_PORT_DIR) \
	   -I$(UCOS_PORT_DIR) \
	   -I$(APP_PORT_DIR) \
	   -I$(APP_PORT_DIR)/OS3 

CC=$(PREFIX)gcc
AS=$(PREFIX)as
AR=$(PREFIX)ar
LD=$(PREFIX)ld
NM=$(PREFIX)nm
OBJDUMP=$(PREFIX)objdump
OBJCOPY=$(PREFIX)objcopy

QEMU=qemu-system-ppc

CFLAGS += -std=c99 -g -nostdlib -DNO_TYPEDEF_OS_FLAGS  

#调试用目录设置
BUILD_DIR= ../../../build


#---------------------------------------------------
#目标uCOS-III.a静态库
#---------------------------------------------------
# 
UCOS_LIB = $(BUILD_DIR)/ucos3.a

#UCOS-III/Source下的源文件
SOURCES_C=$(wildcard $(UCOS_SRC_DIR)/*.c) 
OBJECTS_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_C:.c=.o)))

#UCOS-III/Ports的C源文件
SRC_OS_CPU_C=$(wildcard $(UCOS_PORT_DIR)/*.c) 
OBJ_OS_CPU_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SRC_OS_CPU_C:.c=.o)))

#UCOS-III/Ports的汇编S源文件
SRC_OS_CPU_S=$(wildcard $(UCOS_PORT_DIR)/*.S) 
OBJ_OS_CPU_S=$(addprefix $(BUILD_DIR)/, $(notdir $(SRC_OS_CPU_S:.S=.o)))

#依赖库
#LIB_DEPENDS=$(BUILD_DIR)/$(BSP_SHORT).a 


.PHONY: all ucos clean always

all : ucos

#---------------------------------------------------
#编译uCOS-III库
#---------------------------------------------------
ucos:$(UCOS_LIB)
$(UCOS_LIB): $(OBJECTS_C)  $(OBJ_OS_CPU_C) $(OBJ_OS_CPU_S)
	$(AR) -rcs $@ $^
	

# 编译每个.c文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o: $(UCOS_SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c -g $< -o $@ 

$(BUILD_DIR)/%.o: $(UCOS_PORT_DIR)/%.c
	$(CC)  $(CFLAGS) -c -g $< -o $@ 


# 编译每个.S文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o:  $(UCOS_PORT_DIR)/%.S
	$(CC) $(CFLAGS) -mregnames -c -g $< -o $@ 

clean:
	@rm -f $(UCOS_LIB)
	@rm -f $(OBJECTS_C) 
	@rm -f $(OBJ_OS_CPU_C) 
	@rm -f $(OBJ_OS_CPU_S) 

