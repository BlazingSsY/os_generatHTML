/* verArchCoreComp.s   -   assembly level code for AE653 test harness */

/* Copyright (c) 2000-2006 Verocel, Inc. */

/* Modification history
  --------------------
01f,29May2012,vjw  Removed use of USPRG0
01e,20Mar2012,vjw  Added support for extrended vectors and stub in flash
01d,06Jan2009,vti  Allow TH to be located outside the absolute branch range
01c,25Mar2008,vti  Added support for VerOCode Monitor
01b,22Nov2006,vti  Added support for memory access callbacks.
01a,26Oct2006,vti  Initial version for the e500 architecture.
*/


/*
DESCRIPTION
*/


#define _ASMLANGUAGE
#include "verotrg.h"



/* Mapping of registers */

#define r0  0
#define r2  2
#define r3  3
#define r4  4
#define r5  5
#define r6  6
#define r7  7
#define r8  8
#define r9  9
#define r10  10
#define r11  11
#define r12  12
#define r13  13
#define r29  29
#define r30  30
#define r31  31
#define p5	r8



#define SPRG4  276
#define SPRG5  277
#define SPRG6  278
#define SPRG7  279

#define IVPR   63
#define IVOR6  406
#define IVOR15 415

#define DBSR   304
#define DBCR0  308
#define DBCR1  309
#define DBCR2  310
#define IAC1   312
#define IAC2   313
#define DAC1   316
#define DAC2   317

#define SRR0   26
#define SRR1   27
#define CSRR0  58
#define CSRR1  59
#define ESR    62


/* Book E instrucions */
#define rfci   .long   0x4c000066
#define msync  .long   0x7c0004ac

#define cr0  0


    .extern pdIxCurrent

    .extern verSpyHookAddr


    .data
    .balign 32

    pihRegSaveArea:
         .long      0   /* r28 */
         .long      0   /* SRR0 */
         .long      0   /* SRR1 */

#define PIH_REG_SAVE_R28  0
#define PIH_REG_SAVE_SRR0 4
#define PIH_REG_SAVE_SRR1 8

    dihModeInDBCR0:
         .long   0

    dihInsideCallback:
         .long   0

    dihBrkExpectedCR:
         .long   0
    dihBrkExpectedCRMask:
         .long   0
    dihBrkTrueCount:
         .long   0
    dihBrkFalseCount:
         .long   0
    dihBrkFlashStubCallback:
         .long   0

    .text




/********************************************************************************/
    .globl  _verSpyEnable
    _verSpyEnable:
/********************************************************************************/
/*
   r3 - mode
   r4 - address of byte to be monitored
*/

    stwu    sp, -16(sp)
    mflr    r0
    stw     r0, 20(sp)

    /* set the data break-point address */
    mtspr   316, r4

    /* clear DBCR1 and DBCR2 */
    xor     r4, r4, r4
    mtspr   309, r4
    mtspr   310, r4

    /* calculate mode - settings for DBCR0[DAC1] */
    rlwinm  r3, r3, 18, 12, 13

    /* save the mode (bits as to be set - OR'ed - with DBCR0 */
    lis     r4, dihModeInDBCR0@ha
    stw     r3, dihModeInDBCR0@l(r4)

    /* enable Internal Debug Mode and DAC1 debug events */
    mfspr   r4, 308            /* load DBCR0 */
    rlwinm  r4, r4, 0, 14, 11    /* clear DBCR0[DAC1] */
    or      r4, r4, r3           /* set bits in DBCR0[DAC1] */
    oris    r4, r4, 0x4000       /* set DBCR0[IDM] */
    mtspr   308, r4
    isync

    /* enable debug events in MSR (if not in a Critical Interrupt now) */
    lis     r4, dihInsideCallback@ha
    lwz     r4, dihInsideCallback@l(r4)
    rlwinm. r4, r4, 0, 0, 31
    bne     verSpyDisableRet       /* the Inside Callback flag is set */

      mfmsr   r4
      ori     r4, r4, 0x0200       /* set MSR[DE] */
      mtmsr   r4
      isync

  verSpyDisableRet:
    addi    sp, sp, 16
    blr


/********************************************************************************/
    .globl  _verSpyDisable
    _verSpyDisable:
/********************************************************************************/
    stwu    sp, -16(sp)
    mflr    r0
    stw     r0, 20(sp)

    /* disable Internal Debug Mode and DAC1 debug events */
    mfspr   r3, 308            /* load DBCR0 */
    rlwinm  r3, r3, 0, 14, 11    /* clear DBCR0[DAC1x] */
    rlwinm  r3, r3, 0, 9, 7      /* clear DBCR0[IAC1]  */
    rlwinm  r3, r3, 0, 2, 0      /* clear DBCR0[IDM]   */
    mtspr   308, r3
    isync

    /* disable debug events in MSR */
    mfmsr   r3
    rlwinm  r3, r3, 0, 23, 21    /* clear MSR[DE] */
    mtmsr   r3
    isync

    addi    sp, sp, 16
    blr

