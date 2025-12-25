# Makefile for a "uC-LIB"  on qemu -M ppce500

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
# 目录配置常量定义
#---------------------------------------------------
# 
UC_CPU_INC=../../../Micrium/Software/uC-CPU
UCOS_III_INC=../../../Micrium/Software/uCOS-III/Source
BSP_CFG_INC=../../../DMC/$(BSP)/$(APP)

#链接脚本
LD_SCRIPT=../../../BSP/Startup/$(BSP_SHORT)/gnu/linker/$(LINK_SCRIPT)

#调试用目录设置
BUILD_DIR= ../../../build
#编译目标
UCLIB=$(BUILD_DIR)/uc-lib.a
#---------------------------------------------------
# 编译参数
#---------------------------------------------------
CFLAGS=-I. \
	   -I$(UC_CPU_INC) -I$(UC_CPU_INC)/$(CPU)/GNU \
	   -I$(UCOS_III_INC) \
	   -I$(BSP_CFG_INC)

CC=$(PREFIX)gcc
AS=$(PREFIX)as
AR=$(PREFIX)ar
LD=$(PREFIX)ld
NM=$(PREFIX)nm
OBJDUMP=$(PREFIX)objdump
OBJCOPY=$(PREFIX)objcopy

QEMU=qemu-system-ppc

CFLAGS += -std=c99 -g -DNO_TYPEDEF_OS_FLAGS  

#调试用目录设置
BUILD_DIR= ../../../build

#当前目录uC-LIB下的源文件
SOURCES_C=$(wildcard *.c) 
OBJECTS_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_C:.c=.o)))

.PHONY: all uclib clean always

all : uclib

#---------------------------------------------------
# 目标：uc-lib.a
#---------------------------------------------------
uclib: $(UCLIB)
$(UCLIB): $(OBJECTS_C) 
	$(AR) -rcs $@ $^

# 编译每个.c文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o: %.c
	$(CC)  $(CFLAGS) -c -g $< -o $@ 


clean:
	@rm -f $(UCLIB)
	@rm -f $(OBJECTS_C)


