/*
*********************************************************************************************************
*                                            EXAMPLE CODE
*
*               This file is provided as an example on how to use Micrium products.
*
*               Please feel free to use any application code labeled as 'EXAMPLE CODE' in
*               your application products.  Example code may be used as is, in whole or in
*               part, or may be used as a reference only. This file can be modified as
*               required to meet the end-product requirements.
*
*               Please help us continue to provide the Embedded community with the finest
*               software available.  Your honesty is greatly appreciated.
*
*               You can find our product's user manual, API reference, release notes and
*               more information at https://doc.micrium.com.
*               You can contact us at www.micrium.com.
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*
*                                    MICRIUM BOARD SUPPORT PACKAGE
*                                            MPC574xG-324DS
*
* Filename : bsp_os.c
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*                                             INCLUDE FILES
*********************************************************************************************************
*/

#include  <cpu.h>
#include  "qemu-ppce500.h"

#include  <os.h>
#include  <lib_def.h>

#include  "bsp_os.h"
#include  "bsp_clk.h"
#include  "bsp_int.h"



/*
*********************************************************************************************************
*                                            LOCAL DEFINES
*********************************************************************************************************
*/

#ifndef  OS_CFG_DYN_TICK_EN                                     /* Dynamic tick only available for uCOS-III             */
#define  OS_CFG_DYN_TICK_EN          DEF_DISABLED
#endif



/*
*********************************************************************************************************
*                                            LOCAL DEFINES
*********************************************************************************************************
*/

#if (OS_CFG_DYN_TICK_EN == DEF_ENABLED)
#define  TIMER_COUNT_HZ             ($$$$)                      /* Frequency of the Dynamic Tick Timer.                 */
#define  TIMER_TO_OSTICK(count)     (((CPU_INT64U)(count)  * OS_CFG_TICK_RATE_HZ) /      TIMER_COUNT_HZ)
#define  OSTICK_TO_TIMER(ostick)    (((CPU_INT64U)(ostick) * TIMER_COUNT_HZ)      / OS_CFG_TICK_RATE_HZ)

                                                                /* The max timer count should end on a 1 tick boundary. */
#define  TIMER_COUNT_MAX            (DEF_INT_32U_MAX_VAL - (DEF_INT_32U_MAX_VAL % OSTICK_TO_TIMER(1u)))
#endif



#if (OS_CFG_DYN_TICK_EN == DEF_ENABLED)
static  OS_TICK  TickDelta = 0u;                                /* Stored in OS Tick units.                             */
#endif


/*
*********************************************************************************************************
*                                      LOCAL FUNCTION PROTOTYPES
*********************************************************************************************************
*/

#if (OS_CFG_DYN_TICK_EN == DEF_ENABLED)
static  void  BSP_DynTick_ISRHandler(void);
#endif


static  void  BSP_OS_TickISR(void);


/*
*********************************************************************************************************
*********************************************************************************************************
*                                           GLOBAL FUNCTIONS
*********************************************************************************************************
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*                                          BSP_OS_TickInit()
*
* Description : Initializes the tick interrupt for the OS.
*
* Argument(s) : none.
*
* Return(s)   : none.
*
* Note(s)     : (1) Must be called prior to OSStart() in main().
*
*               (2) This function ensures that the tick interrupt is disabled until BSP_OS_TickEn() is
*                   called in the startup task.
*********************************************************************************************************
*/

void  BSP_OS_TickInit (void)
{   
   /* Configure the timer: TIMER_COUNT_HZ, counter  */
    BSP_IntInit();

    /* Install BSP_Tick_ISRHandler as the int. handler.  */

    
    /* Start the timer.                                     */     
}




/*
*********************************************************************************************************
*                                         BSP_OS_TickEnable()
*
* Description : Enable the OS tick interrupt.
*
* Argument(s) : none.
*
* Return(s)   : none.
*
* Note(s)     : none
*********************************************************************************************************
*/

void  BSP_OS_TickEnable (void)
{
  /* Enable the interrupt.   MSR[EE] = 1, TCR[DIE] = 1         

   CPU_IntEn();                                         
   
    CPU_INT32U  tcr;
    tcr     =  CPU_TCR_Get();  // 读tcr
    tcr    |=  0x04400000;     // TCR[DIE]=1, TCR[ARE]=1
    CPU_TCR_Set(tcr);
    /* $$$$ */                                                  /* Enable Timer interrupt.                              */
    /* $$$$ */                                                  /* Start the Timer count generation.                    */
       
}


/*
*********************************************************************************************************
*                                        BSP_OS_TickDisable()
*
* Description : Disable the OS tick interrupt.
*
* Argument(s) : none.
*
* Return(s)   : none.
*
* Note(s)     : none
*********************************************************************************************************
*/

void  BSP_OS_TickDisable (void)
{
    /*
    CPU_INT32U  tcr;
    tcr     =  CPU_TCR_Get();  // 读tcr
    tcr    &=  0xFBFF;    // TCR[DIE]=0
    CPU_TCR_Set(tcr);
    /* $$$$ */                                                  /* Stop the Timer count generation.                     */
    /* $$$$ */                                                  /* Disable Timer interrupt.                             */
    
}


/*
*********************************************************************************************************
*                                           BSP_OS_TickISR()
*
* Description : Handles the Decriment interrupt.
*
* Argument(s) : none.
*
* Return(s)   : none.
*
* Note(s)     : None.
*********************************************************************************************************
*/

static  void  BSP_OS_TickISR (void)
{
    BSP_TimerAckn();                             
    OSTimeTick();                                        /* Notify the kernel that a tick has occurred.  */
  
}


/*
*********************************************************************************************************
*********************************************************************************************************
**                                      uC/OS-III DYNAMIC TICK
*********************************************************************************************************
*********************************************************************************************************
*/

