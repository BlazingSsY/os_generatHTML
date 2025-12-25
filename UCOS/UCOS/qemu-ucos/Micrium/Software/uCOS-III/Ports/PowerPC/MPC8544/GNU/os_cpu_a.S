/*
*********************************************************************************************************
*                                              uC/OS-III
*                                        The Real-Time Kernel
*
*                    Copyright 2009-2022 Silicon Laboratories Inc. www.silabs.com
*
*                                 SPDX-License-Identifier: APACHE-2.0
*
*               This software is subject to an open source license and is distributed by
*                Silicon Laboratories Inc. pursuant to the terms of the Apache License,
*                    Version 2.0 available at www.apache.org/licenses/LICENSE-2.0.
*
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*
*                                              PowerPC e500
*                                          GNU C/C++ Compiler
*
* File    : os_cpu_a.S
* Version : V3.08.02
*********************************************************************************************************
*/

    .file "os_cpu_a.S"

    .section ".vectors","ax"

#define MACRO0(name)                    .macro  name
#define MACRO1(name, param1)            .macro  name    param1
#define MACRO2(name, param1, param2)    .macro  name    param1    param2
#define CONCAT(left,right)              left##right
#define PARAM(param)                    param

/*
*********************************************************************************************************
*                                          PUBLIC FUNCTIONS
*********************************************************************************************************
*/

    .global  OSStartHighRdy
    .global  OSTaskCtxSw
    .global  OSIntCtxSw
    .global  _vectorbase


/*
*********************************************************************************************************
*                                         EXTERNAL FUNCTIONS
*********************************************************************************************************
*/

    .extern  OSIntEnter
    .extern  OSIntExit
    .extern  BSP_IntHandler
    .extern  OSTaskSwHook
    .extern  IVOR15Handler_Spy

/*
*********************************************************************************************************
*                                         EXTERNAL VARIABLES
*********************************************************************************************************
*/

    .extern  OSRunning
    .extern  OSIntNestingCtr
    .extern  OSTCBCurPtr
    .extern  OSTCBHighRdyPtr
    .extern  OSPrioCur
    .extern  OSPrioHighRdy

/*
*********************************************************************************************************
*                                           LOCAL CONSTANTS
*********************************************************************************************************
*/

    .set    STK_OFFSET_BC,     0
    .set    STK_OFFSET_NEW_LR, STK_OFFSET_BC     + 4
    .set    STK_OFFSET_MSR,    STK_OFFSET_NEW_LR + 4
    .set    STK_OFFSET_PC,     STK_OFFSET_MSR    + 4
    .set    STK_OFFSET_LR,     STK_OFFSET_PC     + 4
    .set    STK_OFFSET_CTR,    STK_OFFSET_LR     + 4
    .set    STK_OFFSET_XER,    STK_OFFSET_CTR    + 4
    .set    STK_OFFSET_CR,     STK_OFFSET_XER    + 4
    .set    STK_OFFSET_USPRG0, STK_OFFSET_CR     + 4
    .set    STK_OFFSET_R0,     STK_OFFSET_USPRG0 + 4
    .set    STK_OFFSET_R2R31,  STK_OFFSET_R0     + 4
    .set    STK_CTX_SIZE,      STK_OFFSET_R2R31  + ( ( 31 - 2 ) + 1 ) * 4


    #define SPRN_IVOR0	0x190	/* Interrupt Vector Offset Register 0 */
    #define SPRN_IVOR1	0x191	/* Interrupt Vector Offset Register 1 */
    #define SPRN_IVOR2	0x192	/* Interrupt Vector Offset Register 2 */
    #define SPRN_IVOR3	0x193	/* Interrupt Vector Offset Register 3 */
    #define SPRN_IVOR4	0x194	/* Interrupt Vector Offset Register 4 */
    #define SPRN_IVOR5	0x195	/* Interrupt Vector Offset Register 5 */
    #define SPRN_IVOR6	0x196	/* Interrupt Vector Offset Register 6 */
    #define SPRN_IVOR7	0x197	/* Interrupt Vector Offset Register 7 */
    #define SPRN_IVOR8	0x198	/* Interrupt Vector Offset Register 8 */
    #define SPRN_IVOR9	0x199	/* Interrupt Vector Offset Register 9 */
    #define SPRN_IVOR10	0x19a	/* Interrupt Vector Offset Register 10 */
    #define SPRN_IVOR11	0x19b	/* Interrupt Vector Offset Register 11 */
    #define SPRN_IVOR12	0x19c	/* Interrupt Vector Offset Register 12 */
    #define SPRN_IVOR13	0x19d	/* Interrupt Vector Offset Register 13 */
    #define SPRN_IVOR14	0x19e	/* Interrupt Vector Offset Register 14 */
    #define SPRN_IVOR15	0x19f	/* Interrupt Vector Offset Register 15 */
/*
*********************************************************************************************************
*                                         OS_CPU_ISR_CRITICAL
*
* Description: This macro is placed at offset 0x0100 in the interrupt-handler table, so it is executed
*              whenever critical interrupts are enabled and the external critical interrupt signal is
*              asserted.  The macro's code saves the current task's context before calling
*              BSP_IntHandler(), which provides further, application-specific processing of the
*              interrupt.
*
*              Critical interrupts are disabled while this routine executes.  However, critical interupts
*              are not disabled when non-critical interrupts occur.  Therefore, this routine checks the
*              return address saved in SSR2 to determine if one of the non-critical ISRs residing in the
*              interrupt-handler table was interrupted.  If the return address indeed corresponds to one
*              of these ISRs, OSIntNestingCtr is not manipulated and the scheduler is not invoked.  These
*              precautions are necessary when a non-critical ISR is interrupted because the interrupt
*              may have occurred before that ISR incremented OSIntNestingCtr, which could result in the
*              ensuing critical ISR prematurely invoking the scheduler.  Whether or not a non-critical
*              ISR was interrupted, though, context is saved and the interrupt is serviced by
*              BSP_IntHandler().
*
*              The interrupted task's context is saved onto its stack as follows:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                           + 0x04     New Link Register
*                                           + 0x08     Machine-State Register
*                                           + 0x0C     Return Address
*                                           + 0x10     Link Register
*                                           + 0x14     Count Register
*                                           + 0x18     Fixed-Point Exception Register
*                                           + 0x1C     Condition Register
*                                           + 0x20     User SPR General-Purpose Register 0
*                                           + 0x24     GPR0
*                                           + 0x28     GPR2
*                                           + 0x2C     GPR3
*                                           + 0x30     GPR4
*                                                   |
*                                                   |
*                                                  \ /
*                                                   V
*                                           + 0x9C     GPR31                        (HIGH MEMORY)
*
*********************************************************************************************************
*/

    MACRO0(OS_CPU_ISR_CRITICAL)
                                                        /* ******* SAVE CURRENT TASK'S CONTEXT ******* */
    stwu    1,-STK_CTX_SIZE(1)                          /* Adjust the stack pointer                    */

    stw     0, STK_OFFSET_R0(1)                         /* Save General-Purpose Register 0             */

    stmw    2, STK_OFFSET_R2R31(1)                      /* Save General-Purpose Registers 2-31         */

    mflr    0
    stw     0, STK_OFFSET_LR(1)                         /* Save the Link Register                      */

    mfctr   0
    stw     0, STK_OFFSET_CTR(1)                        /* Save the Count Register                     */

    mfxer   0
    stw     0, STK_OFFSET_XER(1)                        /* Save the Fixed-Point Exception Register     */

    mfcr    0
    stw     0, STK_OFFSET_CR(1)                         /* Save the Condition Register                 */

    mfspr   0, 0x100
    stw     0, STK_OFFSET_USPRG0(1)                     /* Save User SPR General-Purpose Register 0    */

    mfsrr3  0
    stw     0, STK_OFFSET_MSR(1)                        /* Save the Machine-State Register             */

    mfsrr2  0
    stw     0, STK_OFFSET_PC(1)                         /* Save the return address                     */

                                                        /* See if a non-critical ISR was interrupted   */
    mfivpr  4
    subf    5, 4, 0                                     /* Subtract the IVPR from the return address   */
    cmpli   1, 0, 5, DEBUG_ISR@l                        /* Compare the result to the last offset       */
    lis     0, BSP_IntHandler@h                         /* Load the address of BSP_CriticalIntHandler  */
    ori     0, 0, BSP_IntHandler@l
    mtlr    0
    bc      0x05, 0x04, CRITICAL_CHECK_NESTING          /* Branch if the return address is not in...   */
                                                      /* ...the interrupt-handler table              */
    blrl
    b       CRITICAL_RESTORE_CTX


CRITICAL_CHECK_NESTING:

    lis     4, OSIntNestingCtr@h                        /* See if OSIntNestingCtr == 0                 */
    ori     4, 4, OSIntNestingCtr@l
    lbz     5, 0(4)
    addic.  5, 5, 0
    bc      0x04, 0x02, CRITICAL_INC_NESTING

    lis     6, OSTCBCurPtr@h                            /* Save the current task's stack pointer       */
    ori     6, 6, OSTCBCurPtr@l
    lwz     7, 0(6)
    stw     1, 0(7)

CRITICAL_INC_NESTING:

    addi    5, 5, 1                                     /* Increment OSIntNestingCtr                   */
    stb     5, 0(4)

    blrl                                                /* Call the interrupt controller's handler     */

    lis     0, OSIntExit@h                              /* Call OSIntExit()                            */
    ori     0, 0, OSIntExit@l
    mtlr    0
    blrl

                                                        /* *** RESTORE INTERRUPTED TASK'S CONTEXT **** */
CRITICAL_RESTORE_CTX:
    lwz     0, STK_OFFSET_MSR(1)                        /* Restore the Machine-State Register to SRR3  */
    mtsrr3  0

    lwz     0, STK_OFFSET_PC(1)                         /* Restore the Machine-State Register to SRR2  */
    mtsrr2  0

    lwz     0, STK_OFFSET_USPRG0(1)                     /* Restore User SPR General-Purpose Register 0 */
    mtspr   0x100, 0

    lwz     0, STK_OFFSET_CR(1)                         /* Restore the Condition Register              */
    mtcr    0

    lwz     0, STK_OFFSET_XER(1)                        /* Restore the Fixed-Point Exception Register  */
    mtxer   0

    lwz     0, STK_OFFSET_CTR(1)                        /* Restore the Count Register                  */
    mtctr   0

    lwz     0, STK_OFFSET_LR(1)                         /* Restore the Link Register                   */
    mtlr    0

    lmw     2, STK_OFFSET_R2R31(1)                      /* Restore General-Purpose Registers 2-31      */

    lwz     0, STK_OFFSET_R0(1)                         /* Restore General-Purpose Register 0          */

    addi    1, 1,STK_CTX_SIZE                           /* Adjust the stack pointer                    */

    rfci                                                /* Return to the interrupted task              */

    .endm

/*
*********************************************************************************************************
*                                       OS_CPU_ISR_NON_CRITICAL
*
* Description: This macro is placed at offset 0x0500 in the interrupt-handler table, so it is executed
*              whenever the external non-critical interrupt signal is asserted.  This code saves the
*              current task's context before calling BSP_IntHandler(), which provides further,
*              application-specific processing of the interrupt.
*
*              The interrupted task's context is saved onto its stack as follows:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                           + 0x04     New Link Register
*                                           + 0x08     Machine-State Register
*                                           + 0x0C     Return Address
*                                           + 0x10     Link Register
*                                           + 0x14     Count Register
*                                           + 0x18     Fixed-Point Exception Register
*                                           + 0x1C     Condition Register
*                                           + 0x20     User SPR General-Purpose Register 0
*                                           + 0x24     GPR0
*                                           + 0x28     GPR2
*                                           + 0x2C     GPR3
*                                           + 0x30     GPR4
*                                                   |
*                                                   |
*                                                  \ /
*                                                   V
*                                           + 0x9C     GPR31                        (HIGH MEMORY)
*
*********************************************************************************************************
*/

    MACRO0(OS_CPU_ISR_NON_CRITICAL)
                                                        /* ******* SAVE CURRENT TASK'S CONTEXT ******* */
    stwu    1, -STK_CTX_SIZE(1)                         /* Adjust the stack pointer                    */

    stw     0, STK_OFFSET_R0(1)                         /* Save General-Purpose Register 0             */

    stmw    2, STK_OFFSET_R2R31(1)                      /* Save General-Purpose Registers 2-31         */

    mflr    0
    stw     0, STK_OFFSET_LR(1)                         /* Save the Link Register                      */

    mfctr   0
    stw     0, STK_OFFSET_CTR(1)                        /* Save the Count Register                     */

    mfxer   0
    stw     0, STK_OFFSET_XER(1)                        /* Save the Fixed-Point Exception Register     */

    mfcr    0
    stw     0, STK_OFFSET_CR(1)                         /* Save the Condition Register                 */

    mfspr   0, 0x100
    stw     0, STK_OFFSET_USPRG0(1)                     /* Save User SPR General-Purpose Register 0    */

    mfsrr1  0
    stw     0, STK_OFFSET_MSR(1)                        /* Save the Machine-State Register             */

    mfsrr0  0
    stw     0, STK_OFFSET_PC(1)                         /* Save the return address                     */

    lis     4, OSIntNestingCtr@h                        /* See if OSIntNestingCtr == 0                 */
    ori     4, 4, OSIntNestingCtr@l
    lbz     5, 0(4)
    addic.  5, 5, 0
    bc      0x04, 0x02, NON_CRITICAL_INC_NESTING

    lis     6, OSTCBCurPtr@h                            /* Save the current task's stack pointer       */
    ori     6, 6, OSTCBCurPtr@l
    lwz     7, 0(6)
    stw     1, 0(7)

NON_CRITICAL_INC_NESTING:

    addi    5, 5, 1                                     /* Increment OSIntNestingCtr                   */
    stb     5, 0(4)

    lis     0, BSP_IntHandler@h                         /* Call the interrupt controller's handler     */
    ori     0, 0, BSP_IntHandler@l
    mtlr    0
    blrl

    lis     0, OSIntExit@h                              /* Call OSIntExit()                            */
    ori     0, 0, OSIntExit@l
    mtlr    0
    blrl

                                                        /* *** RESTORE INTERRUPTED TASK'S CONTEXT **** */

    lwz     0, STK_OFFSET_MSR(1)                        /* Restore the Machine-State Register to SRR1  */
    mtsrr1  0

    lwz     0, STK_OFFSET_PC(1)                         /* Restore the return address to SRR0          */
    mtsrr0  0

    lwz     0, STK_OFFSET_USPRG0(1)                     /* Restore User SPR General-Purpose Register 0 */
    mtspr   0x100, 0

    lwz     0, STK_OFFSET_CR(1)                         /* Restore the Condition Register              */
    mtcr    0

    lwz     0, STK_OFFSET_XER(1)                        /* Restore the Fixed-Point Exception Register  */
    mtxer   0

    lwz     0, STK_OFFSET_CTR(1)                        /* Restore the Count Register                  */
    mtctr   0

    lwz     0, STK_OFFSET_LR(1)                         /* Restore the Link Register                   */
    mtlr    0

    lmw     2, STK_OFFSET_R2R31(1)                      /* Restore General-Purpose Registers 2-31      */

    lwz     0, STK_OFFSET_R0(1)                         /* Restore General-Purpose Register 0          */

    addi    1, 1, STK_CTX_SIZE                          /* Adjust the stack pointer                    */

    rfi                                                 /* Return to the interrupted task              */

    .endm

/*
*********************************************************************************************************
*                                             OSTaskCtxSw
*
* Description: Performs a Context switch from a task.  This function is ALWAYS called with interrupts
*              DISABLED.
*
*              OSTaskCtxSw() implements the following pseudo-code:
*
*                  Save CPU registers;
*                  OSTCBCurPtr->OSTCBStkPtr = SP;
*                  OSTaskSwHook();
*                  OSPrioCur = OSPrioHighRdy;
*                  OSTCBCurPtr  = OSTCBHighRdyPtr;
*                  SP        = OSTCBHighRdyPtr->OSTCBStkPtr;
*                  Restore CPU registers
*                  Execute the return-from-interrupt instruction;
*
*
*              The stack frame of the task to suspend will look as follows when OSTaskCtxSw() is done:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                           + 0x04     New Link Register
*                                           + 0x08     Machine-State Register
*                                           + 0x0C     Return Address
*                                           + 0x10     Link Register
*                                           + 0x14     Count Register
*                                           + 0x18     Fixed-Point Exception Register
*                                           + 0x1C     Condition Register
*                                           + 0x20     User SPR General-Purpose Register 0
*                                           + 0x24     GPR0
*                                           + 0x28     GPR2
*                                           + 0x2C     GPR3
*                                           + 0x30     GPR4
*                                                   |
*                                                   |
*                                                  \ /
*                                                   V
*                                           + 0x9C     GPR31                         (HIGH MEMORY)
*
*              The stack frame of the task to resume looks as follows:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                           + 0x04     New Link Register
*                                           + 0x08     Machine-State Register
*                                           + 0x0C     Return Address
*                                           + 0x10     Link Register
*                                           + 0x14     Count Register
*                                           + 0x18     Fixed-Point Exception Register
*                                           + 0x1C     Condition Register
*                                           + 0x20     User SPR General-Purpose Register 0
*                                           + 0x24     GPR0
*                                           + 0x28     GPR2
*                                           + 0x2C     GPR3
*                                           + 0x30     GPR4
*                                                   |
*                                                   |
*                                                  \ /
*                                                   V
*                                           + 0x9C     GPR31                         (HIGH MEMORY)
*
*********************************************************************************************************
*/

    MACRO0(OSTaskCtxSw)
    /*OSTaskCtxSw:*/
                                                        /* ******* SAVE CURRENT TASK'S CONTEXT ******* */
    stwu    1,-STK_CTX_SIZE(1)                          /* Adjust the stack pointer                    */

    stw     0, STK_OFFSET_R0(1)                         /* Save General-Purpose Register 0             */

    stmw    2, STK_OFFSET_R2R31(1)                      /* Save General-Purpose Registers 2-31         */

    mflr    0
    stw     0, STK_OFFSET_LR(1)                         /* Save the Link Register                      */

    mfctr   0
    stw     0, STK_OFFSET_CTR(1)                        /* Save the Count Register                     */

    mfxer   0
    stw     0, STK_OFFSET_XER(1)                        /* Save the Fixed-Point Exception Register     */

    mfcr    0
    stw     0, STK_OFFSET_CR(1)                         /* Save the Condition Register                 */

    mfspr   0, 0x100
    stw     0, STK_OFFSET_USPRG0(1)                     /* Save User SPR General-Purpose Register 0    */

    mfsrr1  0
    stw     0, STK_OFFSET_MSR(1)                        /* Save the Machine-State Register             */

    mfsrr0  0
    stw     0, STK_OFFSET_PC(1)                         /* Save the return address                     */

    lis     4, OSTCBCurPtr@h                            /* Save the current task's stack pointer       */
    ori     4, 4, OSTCBCurPtr@l
    lwz     5, 0(4)
    stw     1, 0(5)

    lis     0, OSTaskSwHook@h                           /* Call OSTaskSwHook()                         */
    ori     0, 0, OSTaskSwHook@l
    mtlr    0
    blrl

    lis     4, OSPrioHighRdy@h                          /* Update the current priority                 */
    ori     4, 4, OSPrioHighRdy@l
    lbz     5, 0(4)
    lis     6, OSPrioCur@h
    ori     6, 6, OSPrioCur@l
    stb     5, 0(6)

    lis     4, OSTCBHighRdyPtr@h                        /* Update the current TCB                      */
    ori     4, 4, OSTCBHighRdyPtr@l
    lwz     5, 0(4)
    lis     6, OSTCBCurPtr@h
    ori     6, 6, OSTCBCurPtr@l
    stw     5, 0(6)

    lwz     1, 0(5)                                     /* Load the new task's stack pointer           */

                                                        /* ******** RESTORE NEW TASK'S CONTEXT ******* */

    lwz     0, STK_OFFSET_MSR(1)                        /* Restore the Machine-State Register to SRR1  */
    mtsrr1  0

    lwz     0, STK_OFFSET_PC(1)                         /* Restore the return address to SRR0          */
    mtsrr0  0

    lwz     0, STK_OFFSET_USPRG0(1)                     /* Restore User SPR General-Purpose Register 0 */
    mtspr   0x100, 0

    lwz     0, STK_OFFSET_CR(1)                         /* Restore the Condition Register              */
    mtcr    0

    lwz     0, STK_OFFSET_XER(1)                        /* Restore the Fixed-Point Exception Register  */
    mtxer   0

    lwz     0, STK_OFFSET_CTR(1)                        /* Restore the Count Register                  */
    mtctr   0

    lwz     0, STK_OFFSET_LR(1)                         /* Restore the Link Register                   */
    mtlr    0

    lmw     2, STK_OFFSET_R2R31(1)                      /* Restore General-Purpose Registers 2-31      */

    lwz     0, STK_OFFSET_R0(1)                         /* Restore General-Purpose Register 0          */

    addi    1, 1, STK_CTX_SIZE                          /* Adjust the stack pointer                    */

    rfi                                                 /* Return to the interrupted task              */

    .endm

/*
*********************************************************************************************************
*                                              OSTickISR
*
* Description: This macro is used to process uC/OS-III tick interrupts, which are produced by the
*              programmable interval timer.  This code saves the current task's context before calling
*              OSTimeTick(), uC/OS-III's CPU-independent routine for processing these interrupts.
*
*              The interrupted task's context is saved onto its stack as follows:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                           + 0x04     New Link Register
*                                           + 0x08     Machine-State Register
*                                           + 0x0C     Return Address
*                                           + 0x10     Link Register
*                                           + 0x14     Count Register
*                                           + 0x18     Fixed-Point Exception Register
*                                           + 0x1C     Condition Register
*                                           + 0x20     User SPR General-Purpose Register
*                                           + 0x24     GPR0
*                                           + 0x28     GPR2
*                                           + 0x2C     GPR3
*                                           + 0x30     GPR4
*                                                   |
*                                                   |
*                                                  \ /
*                                                   V
*                                           + 0x9C     GPR31                        (HIGH MEMORY)
*
*********************************************************************************************************
*/

    MACRO0(OSTickISR)
                                                       /* ******* SAVE CURRENT TASK'S CONTEXT ******* */
    stwu    1, -STK_CTX_SIZE(1)                         /* Adjust the stack pointer                    */

    stw     0, STK_OFFSET_R0(1)                         /* Save General-Purpose Register 0             */

    stmw    2, STK_OFFSET_R2R31(1)                      /* Save General-Purpose Registers 2-31         */

    mflr    0
    stw     0, STK_OFFSET_LR(1)                         /* Save the Link Register                      */

    mfctr   0
    stw     0, STK_OFFSET_CTR(1)                        /* Save the Count Register                     */

    mfxer   0
    stw     0, STK_OFFSET_XER(1)                        /* Save the Fixed-Point Exception Register     */

    mfcr    0
    stw     0, STK_OFFSET_CR(1)                         /* Save the Condition Register                 */

    mfspr   0, 0x100
    stw     0, STK_OFFSET_USPRG0(1)                     /* Save User SPR General-Purpose Register 0    */

    mfsrr1  0
    stw     0, STK_OFFSET_MSR(1)                        /* Save the Machine-State Register             */

    mfsrr0  0
    stw     0, STK_OFFSET_PC(1)                         /* Save the return address                     */

    lis     4, OSIntNestingCtr@h                        /* See if OSIntNestingCtr == 0                 */
    ori     4, 4, OSIntNestingCtr@l
    lbz     5, 0(4)
    addic.  5, 5, 0
    bc      0x04, 0x02, TICK_INC_NESTING

    lis     6, OSTCBCurPtr@h                            /* Save the current task's stack pointer       */
    ori     6, 6, OSTCBCurPtr@l
    lwz     7, 0(6)
    stw     1, 0(7)

TICK_INC_NESTING:

    addi    5, 5, 1                                     /* Increment OSIntNestingCtr                   */
    stb     5, 0(4)

    lis     0, 0x0800                                   /* Clear the PIT interrupt                     */
    mttsr   0

    lis     0, OSTimeTick@h                             /* Call OSTimeTick()                           */
    ori     0, 0, OSTimeTick@l
    mtlr    0
    blrl

    lis     0, OSIntExit@h                              /* Call OSIntExit()                            */
    ori     0, 0, OSIntExit@l
    mtlr    0
    blrl

                                                        /* **** RESTORE INTERRUPTED TASK'S CONTEXT *** */

    lwz     0, STK_OFFSET_MSR(1)                        /* Restore the Machine-State Register to SRR1  */
    mtsrr1  0

    lwz     0, STK_OFFSET_PC(1)                         /* Restore the return address to SRR0          */
    mtsrr0  0

    lwz     0, STK_OFFSET_USPRG0(1)                     /* Restore User SPR General-Purpose Register 0 */
    mtspr   0x100, 0

    lwz     0, STK_OFFSET_CR(1)                         /* Restore the Condition Register              */
    mtcr    0

    lwz     0, STK_OFFSET_XER(1)                        /* Restore the Fixed-Point Exception Register  */
    mtxer   0

    lwz     0, STK_OFFSET_CTR(1)                        /* Restore the Count Register                  */
    mtctr   0

    lwz     0, STK_OFFSET_LR(1)                         /* Restore the Link Register                   */
    mtlr    0

    lmw     2, STK_OFFSET_R2R31(1)                      /* Restore General-Purpose Registers 2-31      */

    lwz     0, STK_OFFSET_R0(1)                         /* Restore General-Purpose Register 0          */

    addi    1, 1, STK_CTX_SIZE                          /* Adjust the stack pointer                    */

    rfi                                                 /* Return to the interrupted task              */

    .endm

/*
*********************************************************************************************************
*                                              IVOR15ISR
*
* Description: This macro is used to process IVOR15 interrupts, which are produced by the
*              hardware.  This code saves the current task's context before calling
*              IVOR15Handler_Spy(), uC/OS-III's CPU-independent routine for processing these interrupts.
*
*              The interrupted task's context is saved onto its stack as follows:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                           + 0x04     New Link Register
*                                           + 0x08     Machine-State Register
*                                           + 0x0C     Return Address
*                                           + 0x10     Link Register
*                                           + 0x14     Count Register
*                                           + 0x18     Fixed-Point Exception Register
*                                           + 0x1C     Condition Register
*                                           + 0x20     User SPR General-Purpose Register
*                                           + 0x24     GPR0
*                                           + 0x28     GPR2
*                                           + 0x2C     GPR3
*                                           + 0x30     GPR4
*                                                   |
*                                                   |
*                                                  \ /
*                                                   V
*                                           + 0x9C     GPR31                        (HIGH MEMORY)
*
*********************************************************************************************************
*/

    MACRO0(IVOR15ISR)
                                                        /* ******* SAVE CURRENT TASK'S CONTEXT ******* */
    stwu    1,-STK_CTX_SIZE(1)                          /* Adjust the stack pointer                    */

    stw     0, STK_OFFSET_R0(1)                         /* Save General-Purpose Register 0             */

    stmw    2, STK_OFFSET_R2R31(1)                      /* Save General-Purpose Registers 2-31         */

    mflr    0
    stw     0, STK_OFFSET_LR(1)                         /* Save the Link Register                      */

    mfctr   0
    stw     0, STK_OFFSET_CTR(1)                        /* Save the Count Register                     */

    mfxer   0
    stw     0, STK_OFFSET_XER(1)                        /* Save the Fixed-Point Exception Register     */

    mfcr    0
    stw     0, STK_OFFSET_CR(1)                         /* Save the Condition Register                 */

    mfspr   0, 0x100
    stw     0, STK_OFFSET_USPRG0(1)                     /* Save User SPR General-Purpose Register 0    */

    mfsrr1  0
    stw     0, STK_OFFSET_MSR(1)                        /* Save the Machine-State Register             */

    mfsrr0  0
    stw     0, STK_OFFSET_PC(1)                         /* Save the return address                     */

    lis     4, OSTCBCurPtr@h                            /* Save the current task's stack pointer       */
    ori     4, 4, OSTCBCurPtr@l
    lwz     5, 0(4)
    stw     1, 0(5)
 
    lis     r3, IVOR15Handler_Spy@h                             /* Call OSTimeTick()                           */
    ori     r3, r3, IVOR15Handler_Spy@l
    mtlr    r3
    blrl

    lis     0, OSIntExit@h                              /* Call OSIntExit()                            */
    ori     0, 0, OSIntExit@l
    mtlr    0
    blrl
                                                        /* **** RESTORE INTERRUPTED TASK'S CONTEXT *** */

    lwz     0, STK_OFFSET_MSR(1)                        /* Restore the Machine-State Register to SRR1  */
    mtsrr1  0

    lwz     0, STK_OFFSET_PC(1)                         /* Restore the return address to SRR0          */
    mtsrr0  0

    lwz     0, STK_OFFSET_USPRG0(1)                     /* Restore User SPR General-Purpose Register 0 */
    mtspr   0x100, 0

    lwz     0, STK_OFFSET_CR(1)                         /* Restore the Condition Register              */
    mtcr    0

    lwz     0, STK_OFFSET_XER(1)                        /* Restore the Fixed-Point Exception Register  */
    mtxer   0

    lwz     0, STK_OFFSET_CTR(1)                        /* Restore the Count Register                  */
    mtctr   0

    lwz     0, STK_OFFSET_LR(1)                         /* Restore the Link Register                   */
    mtlr    0

    lmw     2, STK_OFFSET_R2R31(1)                      /* Restore General-Purpose Registers 2-31      */

    lwz     0, STK_OFFSET_R0(1)                         /* Restore General-Purpose Register 0          */

    addi    1, 1, STK_CTX_SIZE                          /* Adjust the stack pointer                    */

    rfi                                                 /* Return to the interrupted task              */

    .endm


/*
*********************************************************************************************************
*                                        OS_NULL_NON_CRITICAL
*
* Description : This exception handler simply returns to the interrupted code.
*********************************************************************************************************
*/

    MACRO0(OS_NULL_NON_CRITICAL)

    rfi

    .endm

/*
*********************************************************************************************************
*                                          OS_NULL_CRITICAL
*
* Description : This exception handler simply returns to the interrupted code.
*********************************************************************************************************
*/

    MACRO0(OS_NULL_CRITICAL)

    rfci

    .endm

/*
*********************************************************************************************************
*                                 PowerPC e500v2 Interrupt-Handler Table
*
* This is the interrupt-handler table used by the PowerPC to appropriately invoke handlers for various
* types of interrupts.  The interrupts are the results of exceptions, each of which corresponds to an
* offset into this table.  When the interrupt associated with a given expection occurs, the PowerPC adds
* the offset for that exception to this table's base address, which is stored in the Exception-Vector
* Prefix Register (IVPR) by OSStartHighRdy().  The code at the resulting address should represent the
* handler for the exception.
*
* The table entries for the critical input exception (offset 0x0100) and the external input exception
* (offset 0x0500) span 256 (0x100) bytes each, which is enough room to accomodate uC/OS-III's handlers
* for those interrupts, OS_CPU_ISR_CRITICAL() and OS_CPU_ISR_NON_CRITICAL(), respectively.  The entry
* for the programmable-interval timer exception, however, only covers 16 bytes, so OSTickISR(),
* uC/OS-III's handler for timer exceptions, must be placed at another location.  Since the entries at
* offsets 0x1300 and 0x1400 don't correspond to any exceptions, OSTickISR() is placed there, and a
* branch to that location is inserted at offset 0x1000, the actual offset corresponding to the
* programmable-interval timer exception.
*
* All table entries that are not currently used by uC/OS-III contain null routines that simply return
* from the interrupt without performing any actions.  These routines can be replaced if an application
* requires support for additional types of exceptions.
*********************************************************************************************************
*/

    .align 4  
_vectorbase:
    .align 4 

    OS_NULL_NON_CRITICAL

   .org _vectorbase + 0x0100                /* Offset 0x0100 -> Critical Input Exception              */
CRITICAL_INPUT_ISR:
    OS_CPU_ISR_CRITICAL

    .org _vectorbase + 0x0200                /* Offset 0x0200 -> Machine Check Exception               */
MACHINE_CHECK_ISR:
    OS_NULL_CRITICAL

    .org _vectorbase + 0x0300                /* Offset 0x0300 -> Data Storage Exception                */
DATA_STORAGE_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0400                /* Offset 0x0400 -> Instruction Storage Exception         */
INSTRUCTION_STORAGE_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0500                /* Offset 0x0500 -> External Input Exception              */
EXTERNAL_ISR:
    OS_CPU_ISR_NON_CRITICAL

    .org _vectorbase + 0x0600                /* Offset 0x0600 -> Alignment Exception                   */
ALIGNMENT_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0700                /* Offset 0x0700 -> Program Check Exception                     */
PROGRAM_CHK_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0800                /* Offset 0x0800 -> FPU Unavailable Exception             */
FPU_UNAVAILABLE_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0900                  /* Offset 0x0C00 -> System Call Exception                 */ 
SYSTEM_CALL_ISR:
    OSTaskCtxSw

    .org _vectorbase + 0x0A00                  /* Offset 0x0a00 -> Decrementer Exception MSR[EE], TCR[DIE] */
Decrementer_ISR:
    OSTickISR

    .org _vectorbase + 0x0B00                  /* Offset 0x0a00 -> Fixed-interval timer interrupt    */
FIXED_INTERVAL_TIMER_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0C00                /* Offset 0x0C00 ->  Watchdog Timer interrupt            */
WATCHDOG_TIMER_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0D00                /* Offset 0x0C00 ->  DataTLBError Exception                 */
DATA_TLB_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0E00                /* Offset 0x0C00 ->  InstructionTLBError Exception                 */
INSTRUCTION_TLB_MISS_ISR:
    OS_NULL_NON_CRITICAL

    .org _vectorbase + 0x0F00                /* Offset 0x0C00 -> DebugBreakpoint Exception                 */
DEBUG_ISR:
    IVOR15ISR


 /*  END OF .section ".vectors" */
/*
*********************************************************************************************************
*/  
    .section ".text"

/*
*********************************************************************************************************
*                                            OSIntCtxSw()
*
* Description: Performs the Context Switch from an ISR.
*
*              OSIntCtxSw() implements the following pseudo-code:
*
*                  OSTaskSwHook();
*                  OSPrioCur   = OSPrioHighRdy;
*                  OSTCBCurPtr = OSTCBHighRdyPtr;
*                  SP          = OSTCBHighRdyPtr->OSTCBStkPtr;
*                  if (Context saved by Critical ISR) {
*                      Restore MSR and PC to SRR3 and SRR2, respectively;
*                      Restore all other registers;
*                      Execute the return-from-critical-interrupt instruction;
*                  } else {
*                      Restore MSR and PC to SRR1 and SRR0, respectively;
*                      Restore all other registers;
*                      Execute the return-from-interrupt instruction;
*                  }
*
*              Upon entry, the registers of the task being suspended have already been saved onto that
*              task's stack and the SP for the task has been saved in its OS_TCB by the ISR.
*
*              The stack frame of the task to resume is assumed to look as follows:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                        + 0x04     New Link Register
*                                        + 0x08     Machine-State Register
*                                        + 0x0C     Return Address
*                                        + 0x10     Link Register
*                                        + 0x14     Count Register
*                                        + 0x18     Fixed-Point Exception Register
*                                        + 0x1C     Condition Register
*                                        + 0x20     Interrupt type
*                                        + 0x24     GPR0
*                                        + 0x28     GPR2
*                                        + 0x2C     GPR3
*                                        + 0x30     GPR4
*                                                |
*                                                |
*                                               \ /
*                                                V
*                                        + 0x9C     GPR31                        (HIGH MEMORY)
*
* Note(s)    : 1) If the task frame was saved by a critical ISR, the stack entry at offset 0x20 will be
*                 set to 1.
*                 If the task frame was saved by a non-critical ISR, the stack entry at offset 0x20 will
*                 be set to 0.
*********************************************************************************************************
*/

OSIntCtxSw:

    lis     0, OSTaskSwHook@h                           /* Call OSTaskSwHook()                         */
    ori     0, 0, OSTaskSwHook@l
    mtlr    0
    blrl

    lis     4, OSPrioHighRdy@h                          /* Update the current priority                 */
    ori     4, 4, OSPrioHighRdy@l
    lbz     5, 0(4)
    lis     6, OSPrioCur@h
    ori     6, 6, OSPrioCur@l
    stb     5, 0(6)

    lis     4, OSTCBHighRdyPtr@h                        /* Update the current TCB                      */
    ori     4, 4, OSTCBHighRdyPtr@l
    lwz     5, 0(4)
    lis     6, OSTCBCurPtr@h
    ori     6, 6, OSTCBCurPtr@l
    stw     5, 0(6)

    lwz     1, 0(5)                                     /* Load the new task's stack pointer           */

                                                        /* ******** RESTORE NEW TASK'S CONTEXT ******* */

    lwz     0, STK_OFFSET_MSR(1)                        /* Restore the Machine-State Register to SRR1  */
    mtsrr1  0

    lwz     0, STK_OFFSET_PC(1)                         /* Restore the return address to SRR0          */
    mtsrr0  0

    lwz     0, STK_OFFSET_USPRG0(1)                     /* Restore User SPR General-Purpose Register 0 */
    mtspr   0x100, 0

    lwz     0, STK_OFFSET_CR(1)                         /* Restore the Condition Register              */
    mtcr    0

    lwz     0, STK_OFFSET_XER(1)                        /* Restore the Fixed-Point Exception Register  */
    mtxer   0

    lwz     0, STK_OFFSET_CTR(1)                        /* Restore the Count Register                  */
    mtctr   0

    lwz     0, STK_OFFSET_LR(1)                         /* Restore the Link Register                   */
    mtlr    0

    lmw     2, STK_OFFSET_R2R31(1)                      /* Restore General-Purpose Registers 2-31      */

    lwz     0, STK_OFFSET_R0(1)                         /* Restore General-Purpose Register 0          */

    addi    1, 1, STK_CTX_SIZE                          /* Adjust the stack pointer                    */

    rfi                                                 /* Return to the interrupted task              */

/*
*********************************************************************************************************
*                                          OSStartHighRdy()
*
* Description: Starts the highest priority task that is available to run.  OSStartHighRdy() MUST:
*
*              a) Call OSTaskSwHook()
*              b) Set OSRunning to TRUE
*              c) Switch to the highest priority task.
*
*              The stack frame of the task to resume is assumed to look as follows:
*
*              OSTCBHighRdyPtr->OSTCBStkPtr + 0x00     Back chain                    (LOW Memory)
*                                           + 0x04     New Link Register
*                                           + 0x08     Machine-State Register
*                                           + 0x0C     Return Address
*                                           + 0x10     Link Register
*                                           + 0x14     Count Register
*                                           + 0x18     Fixed-Point Exception Register
*                                           + 0x1C     Condition Register
*                                           + 0x20     Interrupt type (initialized to 0x00000000)
*                                           + 0x24     GPR0
*                                           + 0x28     GPR2
*                                           + 0x2C     GPR3
*                                           + 0x30     GPR4
*                                                   |
*                                                   |
*                                                  \ /
*                                                   V
*                                           + 0x9C     GPR31                         (HIGH MEMORY)
*
* Note(s)    : 1) The MSR entry in the stack is initialized so that interrupts will be enabled when the
*                 task begins to run.  In order to allow the interrupts to be properly serviced,
*                 OSStartHighRdy() initializes the Exception-Vector Prefix Register (IVPR) so that it
*                 contains the address of the interrupt-handler table defined above.
*********************************************************************************************************
*/

OSStartHighRdy:

    lis     0, OSTaskSwHook@h                           /* Call OSTaskSwHook()                         */
    ori     0, 0, OSTaskSwHook@l
    mtlr    0
    blrl

    lis     4, OSTCBHighRdyPtr@h                        /* Load the first task's stack pointer         */
    ori     4, 4, OSTCBHighRdyPtr@l
    lwz     5, 0(4)
    lwz     1, 0(5)


    lis     0, _vectorbase@h                            /* Load High part of _vectorbase into r0 */
    mtivpr  0                                           /* Set the IVPR to the value in r0 */

    /* Update IVORs as per relocation */
    li   4, CRITICAL_INPUT_ISR@l
    mtspr SPRN_IVOR0, 4

    li   4, MACHINE_CHECK_ISR@l
    mtspr SPRN_IVOR1, 4

    li   4, DATA_STORAGE_ISR@l
    mtspr SPRN_IVOR2, 4

    li   4, INSTRUCTION_STORAGE_ISR@l
    mtspr SPRN_IVOR3, 4

    li   4, EXTERNAL_ISR@l
    mtspr SPRN_IVOR4, 4

    li   4, ALIGNMENT_ISR@l
    mtspr SPRN_IVOR5, 4

    li   4, PROGRAM_CHK_ISR@l
    mtspr SPRN_IVOR6, 4

    li   4, FPU_UNAVAILABLE_ISR@l
    mtspr SPRN_IVOR7, 4

    li   4, SYSTEM_CALL_ISR@l
    mtspr SPRN_IVOR8, 4

    /* 9: Auxiliary processor unavailable(unsupported) */

    li   4, Decrementer_ISR@l
    mtspr SPRN_IVOR10, 4

    li   4, FIXED_INTERVAL_TIMER_ISR@l
    mtspr SPRN_IVOR11, 4

   li   4, WATCHDOG_TIMER_ISR@l
   mtspr SPRN_IVOR12, 4

   li   4, DATA_TLB_ISR@l
   mtspr SPRN_IVOR13, 4

   li   4, INSTRUCTION_TLB_MISS_ISR@l
   mtspr SPRN_IVOR14, 4

   li   4, DEBUG_ISR@l
   mtspr SPRN_IVOR15, 4
  

    lwz     0, STK_OFFSET_MSR(1)                        /* Restore the Machine-State Register to SRR1  */
    mtsrr1  0

    lwz     0, STK_OFFSET_PC(1)                         /* Restore the return address to SRR0          */
    mtsrr0  0

    lwz     0, STK_OFFSET_USPRG0(1)                     /* Restore User SPR General-Purpose Register 0 */
    mtspr   0x100, 0

    lwz     0, STK_OFFSET_CR(1)                         /* Restore the Condition Register              */
    mtcr    0

    lwz     0, STK_OFFSET_XER(1)                        /* Restore the Fixed-Point Exception Register  */
    mtxer   0

    lwz     0, STK_OFFSET_CTR(1)                        /* Restore the Count Register                  */
    mtctr   0

    lwz     0, STK_OFFSET_LR(1)                         /* Restore the Link Register                   */
    mtlr    0

    lmw     2, STK_OFFSET_R2R31(1)                      /* Restore General-Purpose Registers 2-31      */

    lwz     0, STK_OFFSET_R0(1)                         /* Restore General-Purpose Register 0          */

    addi    1, 1, STK_CTX_SIZE                          /* Adjust the stack pointer                    */

    rfi                                                 /* Start the task                              */

