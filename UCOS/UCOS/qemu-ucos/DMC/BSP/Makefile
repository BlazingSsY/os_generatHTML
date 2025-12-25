# Makefile for a "MPC57XX-BSP & BOOT"  on qemu -M ppce500

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
#LINK_SCRIPT = MPC5646C_FLASH.ld

#---------------------------------------------------
# QEMU-PPCE500 (MPC8544-DS)
#---------------------------------------------------
# 
CPU       = MPC8544
BSP       = MPC8544-QEMU
BSP_SHORT = MPC8544
APP       = mdmc
LINK_SCRIPT = MPC8544_FLASH.ld
#---------------------------------------------------
# 目录配置常量定义
#---------------------------------------------------
# 

BSP_SRC_DIR=./$(BSP)
BOOT_SRC_DIR=./Startup/$(BSP_SHORT)/gnu
LINKER_SCRPT_DIR=./Startup/BSP_SHORT/gnu/linker

#BSP_CLK中引用了UC-LIB中的lib_def
UC-LIB=../../Micrium/Software/uC-LIB

#BSP_INT中引用了UCOS-III中的os.h os_cfg.h os_cpu.h
UCOS-III=../../Micrium/Software/uCOS-III/Source
CFG_CPU_OS=../$(BSP)/$(APP)
UCOS_PORT=../../Micrium/Software/uCOS-III/Ports/PowerPC/$(CPU)/GNU
# UC-LIB引用了UC-CPU中的cpu_def.h cpu_cfg.h
UC-CPU=../../Micrium/Software/uC-CPU

#---------------------------------------------------
# 编译包含路径与选项
#---------------------------------------------------
# 
CFLAGS=-I. \
	   -I$(BSP_SRC_DIR) \
	   -I$(UC-LIB) \
	   -I$(UC-CPU) \
	   -I$(UCOS-III) \
	   -I$(UC-CPU)/$(CPU)/GNU \
	   -I$(CFG_CPU_OS) -I$(CFG_CPU_OS)/OS3 \
	   -I$(UCOS_PORT)


CC=$(PREFIX)gcc
AS=$(PREFIX)as
AR=$(PREFIX)ar
LD=$(PREFIX)ld
NM=$(PREFIX)nm
OBJDUMP=$(PREFIX)objdump
OBJCOPY=$(PREFIX)objcopy

QEMU=qemu-system-ppc

CFLAGS += -std=c99 -g -DNO_TYPEDEF_OS_FLAGS  

#####
#调试用目录设置
BUILD_DIR= ../../build
#---------------------------------------------------
#目标boot和dmc-bsp.a
#---------------------------------------------------
# 
BOOT_BIN =  $(BUILD_DIR)/boot.bin
BOOT_ELF =  $(BUILD_DIR)/boot.elf

BSP_LIB = $(BUILD_DIR)/$(BSP_SHORT).a

#DMC/BSP/MPC574XG-324DS下的源文件
SOURCES_C=$(wildcard $(BSP_SRC_DIR)/*.c) 
OBJECTS_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_C:.c=.o)))

#BOOTLOADER的C源文件
SRC_BOOT_C=$(wildcard $(BOOT_SRC_DIR)/*.c) 
OBJ_BOOT_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SRC_BOOT_C:.c=.o)))

#BOOTLOADER的S汇编源文件
SRC_BOOT_S=$(wildcard $(BOOT_SRC_DIR)/*.S) 
OBJ_BOOT_S=$(addprefix $(BUILD_DIR)/, $(notdir $(SRC_BOOT_S:.S=.o)))

#依赖库
LIB_DEPENDS=$(BUILD_DIR)/ $(BSP_LIB) $(BUILD_DIR)/ucos3.a

.PHONY: all boot $(BSP_LIB) clean always

all : bsp

#---------------------------------------------------
#编译boot.bin 与 boot.elf (注：这部分需要与应用一起联编)
#---------------------------------------------------
boot:$(BOOT_BIN)
$(BOOT_BIN) : $(BOOT_ELF)
	$(OBJCOPY) -O binary  $< $@
$(BOOT_ELF): $(OBJ_BOOT_C)  $(OBJ_BOOT_S) \
						 $(LIB_DEPENDS) \
						$(LINKER_SCRPT_DIR)/(LINK_SCRIPT)
	$(LD) -T $(LINKER_SCRPT_DIR)/(LINK_SCRIPT)  \
	      -Map=$(BUILD_DIR)/boot.map -o $@ $^


#---------------------------------------------------
#编译BSP中的CLK/LED/INT/ADC/FLASH/串口等
#---------------------------------------------------
bsp: $(BSP_LIB)
# 创建BSP库，将所有对象文件打包成静态库
$(BSP_LIB): $(OBJECTS_C)  $(OBJ_BOOT_C)  $(OBJ_BOOT_S)
	$(AR) -rcs $@ $^

# 编译每个.c文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o: $(BSP_SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# 编译每个.c文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o: $(BOOT_SRC_DIR)/%.c
	$(CC)   $(CFLAGS) -mregnames -c -g $< -o $@ 

# 编译每个.S文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o:  $(BOOT_SRC_DIR)/%.S
	$(CC)  -mregnames -c -g $< -o $@ 


clean:
	@rm -f $(OBJECTS_C) $(BSP_LIB) $(BOOT_BIN) $(BOOT_ELF)
	@rm -f $(OBJ_BOOT_S) 
	@rm -f $(OBJ_BOOT_C) 
	


