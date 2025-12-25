# config.mk - default makefile definitions
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
#
# DESCRIPTION
# This file is included in Makefiles to establish defaults. The Makefiles may
# customize these definitions to suit the circumstance.
#
# Redefinitions of make variables earlier than the include of this file will
# have no affect.
#


# default CPU
CPU=x86-win32
#

export CFLAGS = -std=c99 -D__WIN32__ -g -DNO_TYPEDEF_OS_FLAGS  
export ASMFLAGS =
export CC = gcc
export CXX = g++
export LD = gcc
export ASM = nasm
export LDFLAGS = -L./lib
export LIBS = 
export MINGW_LIB=/mingw/lib


export BUILD_DIR = $(abspath build)

# Path for uCOS  source files 
export UCOS_CORE_SRC=Micrium/Software/uCOS-III/Source
export UC_LIB_SRC=Micrium/Software/uC-Lib
export UC_CPU_SRC=Micrium/Software/uC-CPU


#Path for uCOS-III WIN32 port source files 
export UC_PORT_COMPILER_SRC=Micrium/Software/uC-CPU/Win32/Visual_Studio    # target CPU compiler specific
export UC_PORT_BSP_SRC=Microsoft/BSP/Windows                               # target specific
export UCOS_PORT_APP_SRC=Microsoft/Windows/Kernel                          # Application Sources

#include directory for compile
export UCOS_INCLUDE_DIR= Micrium/Software/uC-CPU \
                    Micrium/Software/uC-CPU/Win32/Visual_Studio \
                    Micrium/Software/uC-LIB \
                    Micrium/Software/uCOS-III/Ports/Win32/Visual_Studio \
					Micrium/Software/uCOS-III \
                    Micrium/Software/uCOS-III/Source \
                     Microsoft/Windows/Kernel 