# Makefile for a "MPC57XX-AppInit (bootApp)"  on qemu -M ppce500

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
LINK_SCRIPT = MPC8544_RAM.ld

#---------------------------------------------------
# 目录配置常量定义
#---------------------------------------------------
# 
APP_CPU_LIB_CFG=../
OS_APP_CFG=./

BSP_INC=../../../BSP/$(BSP)
UC_CPU_INC=../../../../Micrium/Software/uC-CPU
UCOS_III_INC=../../../../Micrium/Software/uCOS-III/Source
UC_LIB_INC=../../../../Micrium/Software/uC-LIB
PORT_UCOS_INC = ../../../../Micrium/Software/uCOS-III/Ports/PowerPC/$(CPU)/GNU
TA_INC = ./TA

#生成可加装文件的链接脚本
LD_SCRIPT=../../../BSP/Startup/$(BSP_SHORT)/gnu/linker/$(LINK_SCRIPT)
#LD_SCRIPT=../../../BSP/Startup/MPC5748G/gnu/linker/56xx_flash.ld 
#调试用目录设置
BUILD_DIR= ../../../../build

#---------------------------------------------------
#依赖库
#---------------------------------------------------
BSP_LIB = $(BUILD_DIR)/$(BSP_SHORT).a
UCPU_LIB = $(BUILD_DIR)/uc-cpu.a
UC_LIB  = $(BUILD_DIR)/uc-lib.a
UCOSIII_LIB = $(BUILD_DIR)/ucos3.a

VSMONIOTR_OBJ = $(BUILD_DIR)/VeroMon.o
#UDP_OBJ = $(BUILD_DIR)/libnet.a
#---------------------------------------------------
# 编译包含路径与选项
#---------------------------------------------------
# 
#参考:ppc-freevle-eabi-gcc -c -mcpu=e200z0 -meabi -msdata=none -mregnames -mvle -O2 -gdwarf-2 -fomit-frame-pointer -falign-functions=16 -mno-spe -msoft-float -fno-gcse -ffunction-sections -fdata-sections -fno-common -Wall -Wextra -Wstrict-prototypes -Wa,-alms=build/lst/ -DPPC_USE_VLE=1 -MD -MP -MF .dep/build.d -I. 
CFLAGS=-I. -I../ \
	   -I$(BSP_INC) \
	   -I$(UC_CPU_INC) -I$(UC_CPU_INC)/$(CPU)/GNU \
	   -I$(UCOS_III_INC) \
	   -I$(UC_LIB_INC) \
	   -I$(PORT_UCOS_INC) \
	   -I$(TA_INC)
#
#引用其他的
#-mcpu=e200z4 -meabi -msdata=none -mregnames -mvle -O2 -gdwarf-2 -fomit-frame-pointer -falign-functions=16 -mno-spe -msoft-float -fno-gcse -ffunction-sections -fdata-sections -fno-common -Wall -Wextra -Wstrict-prototypes -Wa,-alms=build/lst/ -DPPC_USE_VLE=1 -MD -MP -MF .dep/build.d 
#

CFLAGS +=  -std=c99 -g -meabi   -nostdlib -Wimplicit-function-declaration 

LDFLAGS =   --no-whole-archive -Map=$(BUILD_DIR)/bootApp.map  


CC=$(PREFIX)gcc
AS=$(PREFIX)as
AR=$(PREFIX)ar
LD=$(PREFIX)ld
NM=$(PREFIX)nm
OBJDUMP=$(PREFIX)objdump
OBJCOPY=$(PREFIX)objcopy

QEMU=qemu-system-ppc

#---------------------------------------------------
#目标bootApp
#---------------------------------------------------
# 
MKIMAGE     =  $(BUILD_DIR)/./mkimage
UCOS_IMAGE   =  $(BUILD_DIR)/uImage
BOOT_APP_BIN =  $(BUILD_DIR)/bootApp.bin
BOOT_APP_ELF =  $(BUILD_DIR)/bootApp.elf

# MPC574XG上的UCOSIII应用源文件(.C)
SOURCES_C=$(wildcard *.c) 
OBJECTS_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_C:.c=.o)))
SOURCES_TA_C=$(wildcard TA/*.c)
OBJECTS_TA_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_TA_C:.c=.o)))
SOURCES_TP_C = $(shell find TP/ -type f -name "*.c")
OBJECTS_TP_C = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_TP_C:.c=.o)))
SOURCES_TA_S=$(wildcard TA/*.s)
OBJECTS_TA_S = $(addprefix $(BUILD_DIR)/, $(notdir $(SOURCES_TA_S:.s=.o)))

#依赖静态库
LIB_DEPENDS=  $(UC_LIB) $(UCOSIII_LIB) $(BSP_LIB) $(UCPU_LIB) 

.PHONY: all bootApp clean always

all : uImage
#---------------------------------------------------
#编译boot.bin 与 boot.elf，生成uImage
#---------------------------------------------------
uImage:$(UCOS_IMAGE)
$(UCOS_IMAGE): $(BOOT_APP_BIN)
	$(MKIMAGE) -A ppc -O linux -T kernel -C none -a 0x00000000 -e 0x00000000 -n 'ucos Kernel' -d $< $@
#	$(MKIMAGE) -A ppc -O linux -T kernel -C none -a 0x00000000 -e 0x00000000 -n 'ucos Kernel' -d $(BOOT_APP_BIN) $(UCOS_IMAGE)

$(BOOT_APP_BIN) : $(BOOT_APP_ELF) 
	$(OBJCOPY) -O binary  $< $@

$(BOOT_APP_ELF): $(OBJECTS_C) $(OBJECTS_TA_C) $(OBJECTS_TA_S) $(OBJECTS_TP_C) $(BUILD_DIR)/cpu_a.o
	$(LD) $(LDFLAGS)  -T $(LD_SCRIPT)  -o $@ $^   --start-group $(LIB_DEPENDS) --end-group  -no-whole-archive  

# 编译每个.c文件为.o文件，并将.o文件放置在BUILD_DIR目录下
$(BUILD_DIR)/%.o: %.c
	$(CC)  $(CFLAGS) -c -g $< -o $@  -MD -MF $(@:.o=.d)

$(BUILD_DIR)/%.o: TA/%.c
	$(CC)  $(CFLAGS) -c -g $< -o $@  -MD -MF $(@:.o=.d)

$(BUILD_DIR)/%.o: TA/%.s
	$(CC) $(CFLAGS)  -mcpu=powerpc -mno-altivec -fPIC -mregnames -c -g $< -o $@


define generate_rule
$(BUILD_DIR)/$(notdir $(1:.c=.o)): $(1)
	$(CC) $(CFLAGS) -c -g $$< -o $$@ -MD -MF $$(@:.o=.d)
endef

$(foreach src,$(SOURCES_TP_C),$(eval $(call generate_rule,$(src))))

debug:
	qemu-system-ppc -M ppce500 -nographic -bios $(BUILD_DIR)/u-boot -kernel $(UCOS_IMAGE) -serial mon:stdio -s -S

clean:
	@rm -f $(BOOT_APP_BIN) $(BOOT_APP_ELF) 
	@rm -f $(BUILD_DIR)/bootApp.map 
	@rm -f $(OBJECTS_C) $(OBJECTS_TA_C) $(OBJECTS_TP_C)
	


