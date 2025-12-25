/*
*********************************************************************************************************
*
*                                    MICRIUM BOARD SUPPORT PACKAGE
*                                            MPC574xG-324DS
*
* Filename : bsp_int.c
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*                                             INCLUDE FILES
*********************************************************************************************************
*/

#include  "processor.h"
#include  "qemu-ppce500.h"
#include  "bsp_clk.h"
#include  "bsp_int.h"



/*---------------------------------------------------------------------------*/
/* Inline Assembler Defines                                                  */
/*---------------------------------------------------------------------------*/

/* This is the interrupt service routine table used in software mode.
   The INTC supports 4 bytes or 8 byte entries, we will use 4 byte entries.
   The 4/8 bytes mode is configured in INTC_InitINTCInterrupts.
*/
#define  BSP_INT_VECT_TBL_SIZE           278*4  
#define  BSP_INT_MAX_PRIO                0xFu

# define __iomem
/* from cpu.h for avoid error 'undefined reference' */

extern void CPU_DECAR_Set(CPU_INT32U cnt);      
extern void CPU_TBL_Set(CPU_INT32U cnt);     
extern void CPU_DEC_Set(CPU_INT32U cnt);   
extern void CPU_TCR_Set(CPU_INT32U cnt);   
extern void CPU_HID0_Set(CPU_INT32U cnt);   

extern CPU_INT32U CPU_DECAR_Get();      
extern CPU_INT32U CPU_TBL_Get();      
extern CPU_INT32U CPU_DEC_Get();   
extern CPU_INT32U CPU_TCR_Get();    
extern CPU_INT32U CPU_HID0_Get();   
extern void        BSP_Tick_Init();

extern unsigned  decrementer_max ;
extern unsigned  decrementer_count;

static __inline__ unsigned int get_dec (void)
{
	unsigned int val;

	__asm__ volatile ("mfdec %0":"=r" (val):);

	return val;
}

static __inline__ void set_dec (unsigned int *val)
{
	if (val)
		__asm__ volatile ("mtdec %0"::"r" (*val));
}

static __inline__ void set_tsr(unsigned long val)
{
	__asm__ volatile("mtspr 0x150, %0" : : "r" (val));
}

static __inline__ unsigned long get_esr(void)
{
	unsigned long val;
	__asm__ volatile("mfspr %0, 0x03e" : "=r" (val) :);
	return val;
}

static inline unsigned long get_msr(void)
{
	unsigned long msr;

	__asm__ volatile ("mfmsr %0" : "=r" (msr) : );

	return msr;
}



static inline void set_msr(unsigned long msr)
{
	__asm__ volatile ("mtmsr %0" : : "r" (msr));
}

static inline u32 in_be32(const volatile unsigned __iomem *addr)
{
	u32 ret;

	__asm__ __volatile__("sync; lwz%U1%X1 %0,%1;\n"
			     "twi 0,%0,0;\n"
			     "isync" : "=r" (ret) : "m" (*addr));
	return ret;
}

static inline void out_be32(volatile unsigned __iomem *addr, u32 val)
{
	__asm__ __volatile__("sync; stw%U0%X0 %1,%0" : "=m" (*addr) : "r" (val));
}

static void PITException()
{
	/*
	 * Reset PIT interrupt
	 */
	set_tsr(0x0c000000);

	/*
	 * Call timer_interrupt routine in interrupts.c
	 */
	my_timer_interrupt(0);
}



/*
*********************************************************************************************************
*                                          LOCAL DATA TYPES
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*                                        BSP_IntInit()
*
* Description : BSP_IntInit.
*
* Argument(s) : none.
*
* Return(s)   : none.
*
* Note(s)     : none.
*********************************************************************************************************
*/
void BSP_IntInit (void)
{
    
    BSP_Tick_Init();
	
    /* reset mpc85xx pic */
    ccsr_pic_t __iomem *pic = (void *)CFG_SYS_MPC8xxx_PIC_ADDR;
	out_be32(&pic->gcr, MPC85xx_PICGCR_RST);
	while (in_be32(&pic->gcr) & MPC85xx_PICGCR_RST) /*wait for pic reset finished* */
		;
	out_be32(&pic->gcr, MPC85xx_PICGCR_M);
	in_be32(&pic->gcr);

    /* hz per tick */
	set_dec (&decrementer_count);
	set_msr (get_msr () | MSR_EE);

    
}
void set_vector_handler()
{
	
}

/* returns flag if MSR_EE was set before */
CPU_INT32U BSP_IntEn(void)
{
	CPU_INT32U msr = get_msr ();

	set_msr (msr & ~MSR_EE);
	return ((msr & MSR_EE) != 0);
}


void BSP_IntDis(void)
{
	set_msr (get_msr () | MSR_EE);
}

void BSP_TimerAckn()
{
	/* call cpu specific function from $(CPU)/interrupts.c */
	mtspr(SPRN_TSR, TSR_PIS);;

	/* Restore Decrementer Count */

	set_dec (&decrementer_count);
}



/*
*********************************************************************************************************
*                                            timer_interrupt(struct pt_regs * regs)
*
* Description :  u-boot中注册的Decrementer中断处理函数名称.
*
* Argument(s) : regs     
*
*
* Return(s)   : none.
*
* Note(s)     : none.
*********************************************************************************************************
*/

void my_timer_interrupt()
{
   
                                         /* ---- INTERRUPTS ARE DISABLED BEFORE WE GET HERE ---- */
    BSP_TimerAckn();                           /* Acknowledge the interrupt.                           */

    OSIntEnter();                                           /* Increment the nesting counter.                       */

    CPU_IntEn();                                            /* Allow interrupt nesting.                             */
   
    BSP_TmrTickIntHandler(); 								/* 调用decrementer interrupt 处理函数*/
   
    CPU_MB();                                               /* Ensure that the interrupt flag was cleared.          */
    CPU_IntDis();
    set_dec(&decrementer_max); ;                          /* Signal the end of interrupt.                         */        OSIntExit();                                            /* Decrement nesting counter. Context switch if 0.      */
	OSIntExit();  

 
 
}


/**
 * 执行上下文保存os_cpu_a.S，然后再调用OS的OSTimeTick函数，用于任务队列调度
 */
void BSP_TmrTickIntHandler(void) 
{	
	
}

/**
 * 外部硬件中断处理，暂时未处理...
 */
void  BSP_IntHandler (void)
{
	  while (1u) {
       CPU_NOP(); 
    }
}


/*
*********************************************************************************************************
*                                        SWT_disable()
*
* Description : SWT_disable.
*
* Argument(s) : none.
*
* Return(s)   : none.
*
* Note(s)     : none.
*********************************************************************************************************
*/
void SWT_disable(void)
{
    CPU_INT32U  tcr;
    tcr     =  CPU_TCR_Get();  // 读tcr
    tcr    =  tcr & 0xF7FF;    // TCR[WIE]=0
    CPU_TCR_Set(tcr);
}//SWT_disable

