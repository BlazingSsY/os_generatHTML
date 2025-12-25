#********************************************************************************************************
#                                               uC/CPU
#                                    CPU CONFIGURATION & PORT LAYER
#
#                    Copyright 2004-2021 Silicon Laboratories Inc. www.silabs.com
#
#                                 SPDX-License-Identifier: APACHE-2.0
#
#               This software is subject to an open source license and is distributed by
#                Silicon Laboratories Inc. pursuant to the terms of the Apache License,
#                    Version 2.0 available at www.apache.org/licenses/LICENSE-2.0.
#
#********************************************************************************************************

#********************************************************************************************************
#
#                                      CPU CACHE IMPLEMENTATION
#                                         PowerPC e500v2
#                                              L1 Cache
#                                           GNU C Compiler
#
# Filename : cpu_cache_powerpc_e500v2.c
# Version  : V1.32.01
#********************************************************************************************************


#********************************************************************************************************
#                                           PUBLIC FUNCTIONS
#********************************************************************************************************

    .global     CPU_DCache_LineSizeGet
    .global     CPU_DCache_RangeInv
    .global     CPU_DCache_RangeFlush


#********************************************************************************************************
#                                                EXTERNS
#********************************************************************************************************

    .extern     CPU_Cache_Linesize


#********************************************************************************************************
#                                           MACROS AND DEFINIITIONS
#********************************************************************************************************

    .equ        L1CFG0,     515


#********************************************************************************************************
#                                      CODE GENERATION DIRECTIVES
#********************************************************************************************************

    .section    .text


#********************************************************************************************************
#                                           CPU_DCache_LineSizeGet()
#
# Description : Returns the cache line size.
#
# Prototypes  : void  CPU_DCache_LineSizeGet (void)
#
# Argument(s) : none.
#********************************************************************************************************

CPU_DCache_LineSizeGet:
    mfspr       r0, L1CFG0                                      # CBSIZE is in L1CFG0[39-40]
    rlwinm    r0, r0, 9, 30, 31                               # Move CBSIZE into R0[62-63] and mask other bits to zero

    li        r3, 32                                          # Line size is 32 << CBSIZE, 0 <= CBSIZE <= 2

    rlwinm    r3, r3, 0, 0, 31                                
    rlwinm    r3, r3, r0, 0, 31                               

    blr                                                      # Return the line size in R3


#********************************************************************************************************
#                                      INVALIDATE DATA CACHE RANGE
#
# Description : Invalidate a range of data cache.
#
# Prototypes  : void  CPU_DCache_RangeInv  (void       *p_mem,
#                                           CPU_SIZE_T  range);
#
# Argument(s) : p_mem    Start address of the region to invalidate.
#
#               range    Size of the region to invalidate in bytes.
#
# Note(s)     : none.
#********************************************************************************************************

CPU_DCache_RangeInv:
    cmplwi    r4, 0                                           # If the range is 0, do nothing
    beq       InvReturn                                       # ...

    mfmsr       r0                                              # Save MSR and disable interrupts
    wrteei      0
    sync                                                        # Complete data operations before invalidation

    lis       r11, CPU_Cache_Linesize@ha                      # Store the line size into R11
    lwz       r11, CPU_Cache_Linesize@l(r11)                  # ...

    neg         r12, r11                                        # The line size is a power of 2; form a mask for the lower bits

    neg         r4, r4                                          # Pad the range so it is a multiple of the line size
    and         r4, r4, r12                                     # ...
    neg.        r4, r4                                          # Check if the result underflowed
    bne       InvRangeNotOV                                   # If it did not, we are finished with the range

    li          r4, 0x0000
    ori         r4, r4, 0xFFFF    
    rlwinm     r4, r4, 0, 0, 15  
    and        r4, r4, r12       

InvRangeNotOV:
    and         r3, r3, r12                                     # Align the address to the start of the cache line

    xor         r12, r12, r12                                   # R12 will count how much memory has been invalidated
InvLine:
    cmpw        r12, r4                                         # Have we invalidated the entire range?
    beq       InvEnd                                          # If so, we can return

    dcbf        r3, r12                                         # Invalidate the cache line

    add         r12, r12, r11                                   # Move to the next cache line
    b        InvLine                                         # ...

InvEnd:
    sync
    wrtee       r0                                              # Restore MSR

InvReturn:
    blr


#********************************************************************************************************
#                                       FLUSH DATA CACHE RANGE
#
# Description : Flush (clean) a range of data cache.
#
# Prototypes  : void  CPU_DCache_RangeFlush  (void       *p_mem,
#                                             CPU_SIZE_T  range)
#
# Argument(s) : p_mem    Start address of the region to flush.
#
#               range    Size of the region to invalidate in bytes.
#
# Note(s)     : none.
#********************************************************************************************************

CPU_DCache_RangeFlush:
    cmplwi    r4, 0                                           # If the range is 0, do nothing
    beq       FlushReturn                                     # ...

    mfmsr       r0                                              # Save MSR and disable interrupts
    wrteei      0
    sync                                                        # Complete data operations before clean

    lis       r11, CPU_Cache_Linesize@ha                      # Store the line size into R11
    lwz       r11, CPU_Cache_Linesize@l(r11)                  # ...

    neg         r12, r11                                        # The line size is a power of 2; form a mask for the lower bits

    neg         r4, r4                                          # Pad the range so it is a multiple of the line size
    and         r4, r4, r12                                     # ...
    neg.        r4, r4                                          # Check if the result underflowed
    bne       FlushRangeNotOV                                 # If it did not, we are finished with the range

    li          r4, 0x0000
    ori         r4, r4, 0xFFFF  
          
    rlwinm     r4, r4, 0, 0, 15  
    and        r4, r4, r12       

FlushRangeNotOV:
    and         r3, r3, r12                                     # Align the address to the start of the cache line

    xor         r12, r12, r12                                   # R12 will count how much memory has been cleaned
FlushLine:
    cmpw        r12, r4                                         # Have we cleaned the entire range?
    beq       FlushEnd                                        # If so, we can return

    dcbst       r3, r12                                         # Clean the cache line

    add         r12, r12, r11                                   # Move to the next cache line
    b        FlushLine                                       # ...

FlushEnd:
    sync
    wrtee       r0                                              # Restore MSR

FlushReturn:
    blr
