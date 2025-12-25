#
# Copyright (c) 2024-2027 avic, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable avic license agreement.
#
# modification history
# --------------------
# 01a,16sept24,guqf   created

include build_scripts/config.mk

.PHONY: all ucos_win32 uc-lib uc-os uc-cpu   clean always 

all: ucos_win32 uc-lib uc-os uc-cpu  

#
# ucos_app
#
ucos_win32: $(BUILD_DIR)/ucos-app.exe 
$(BUILD_DIR)/ucos-app.exe:uc-lib uc-os uc-cpu 
	@$(MAKE) -C Microsoft/Windows/Kernel/OS3 BUILD_DIR=$(abspath $(BUILD_DIR))
	

#
# uc-cpu 
#
uc-cpu: $(BUILD_DIR)/uc-cpu.a
$(BUILD_DIR)/uc-cpu.a:always
	@$(MAKE) -C Micrium/Software/uC-CPU BUILD_DIR=$(abspath $(BUILD_DIR))

#
# uc-os 
uc-os: $(BUILD_DIR)/uc-os.a
$(BUILD_DIR)/uc-os.a:always
	@$(MAKE) -C Micrium/Software/uCOS-III/Source BUILD_DIR=$(abspath $(BUILD_DIR))

#
# uc-lib 
#
uc-lib: $(BUILD_DIR)/uc-lib.a
$(BUILD_DIR)/uc-lib.a:always
	@$(MAKE) -C Micrium/Software/uC-LIB BUILD_DIR=$(abspath $(BUILD_DIR))


#
# Always
#
always:
	@mkdir -p $(BUILD_DIR)

#
# Clean
#
clean:
	@$(MAKE) -C Micrium/Software/uC-CPU BUILD_DIR=$(abspath $(BUILD_DIR)) clean
	@$(MAKE) -C Micrium/Software/uC-LIB BUILD_DIR=$(abspath $(BUILD_DIR)) clean
	@$(MAKE) -C Micrium/Software/uCOS-III/Source BUILD_DIR=$(abspath $(BUILD_DIR)) clean
	@rm -rf $(BUILD_DIR)/*
