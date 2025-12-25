/* usrTargetAgent.c - TH initialization */

/* Copyright 2006-2007 Verocel, Inc. */

/*
modification history
--------------------
01b,07dec07,vjw Added support coverage only one partition
01a,28sep06,vjw  Created
*/

/*
DESCRIPTION

This library configures and initializes TH
*/


#include "time.h"
#include "verotrg.h"
#include "stdio.h"
#include <string.h>
#include  <os.h>
#include  "app_cfg.h"
#include "THPL.h"
#include "THCL.h"

//#define _WRS_ASM(x)		__asm__ volatile (x)

#define THPL_TASK_STK_SIZE       2048
#define THPL_TASK_PRIORITY       10
#define THPL_TASK_DELAY          20
#define THPL_IO_TIME_OUT         1000
#define TEST_TASK_STK_SIZE       2048
#define TEST_TASK_PRIORITY       10
#define TEST_TASK_DELAY          10


/*****task parameter**********/
OS_TCB THPLTask_TCB; // tcb
CPU_STK THPLTask_STK[THPL_TASK_STK_SIZE + 64]; //STK
OS_TCB testTask_TCB; // tcb
CPU_STK testTask_STK[THPL_TASK_STK_SIZE + 64]; //STK



/**********************parameter for run TP**************************************************/
typedef void (*tp_Fn_ptr)(void);
char resultBuf[VER_MSG_MAX_LEN * 8 + 4] = {0};
int  resultBufLen = VER_MSG_MAX_LEN * 8;
static char * lastLine=NULL;
UINT32 testParam1 = 0;
UINT32 testParam2 = 0;
int testMode = -1;
tp_Fn_ptr volatile testProgram = NULL;
BOOL volatile testReadyToRun = FALSE;
int volatile currSummary = -1;


//static int testTimeout = 30; /* timeout in sec, test task runtime, */
                               /*it is used for watchdog timeout set in wxworks, */ 
                               /*currently, ucos doesn't has such funtion, so we just comment out it */
                               /*it will be reused once ucos has that funtion */


 

/**the following function are empty as no exact requirement to implement it, just keep it here******/
void verBeforeTestLoad(void *param1, void *param2)
{
/**it should be a hook function，and store in verotrg.c***/
/**but we didn't have clear requirement now, just keep it hear***/

}

void wdStart()
{
	/**it should be a hook function，and store in verotrg.c***/
	/**but we didn't have clear requirement now, just keep it hear***/
}

void wdCancel()
{
	/**it should be a hook function，and store in verotrg.c***/
	/**but we didn't have clear requirement now, just keep it hear***/
}

void tmBeforeTestRunHook(int param1, int param2)
{
}

void tmAfterTestRunHook(int param1, int param2)
{
}
/**the upper function are empty as no exact requirement to implement it, just keep it here******/



static void hardReset() 
{
    //reboot(0);
} 


void ResetTestProgram()
{	  
	/* reset the addr for test program */
	testProgram = NULL;
}

int startTest()
{
	OS_ERR os_err;
    int i = 10;
    currSummary = 1;
    testReadyToRun = TRUE;
    while(i > 0)
    {
        if(currSummary > 0)
        {
            OSTimeDly(THPL_TASK_DELAY, OS_OPT_TIME_DLY, &os_err);
        }
		else
		{
            break;
		}
        i--;
    }
    testReadyToRun = FALSE;
    if(currSummary > 0)
    {
        currSummary = -1;
        return 1;
    }
	return 0;    
}

/* Test harness commands */
static void RunTest(int mode, int parts)
{
    BOOL testOK = TRUE;
    testMode = mode;
    wdStart();
    #if 1
    if(testProgram)
    {
        testProgram();
    }
    else
    {
        testOK = FALSE;
    }
    #endif
    #if 0
    if(startTest())
    {
        testOK = FALSE;
    }
    #endif
    wdCancel();
    ResetTestProgram();

    /* send acknowladge message */
    if(testOK)
    {
        THPLSendAckMsg(THPL_OK);
    }
    else
    {
        THPLSendNackMsg(THPL_ERROR);
    }
}


static void Report(int repeat, void *param2)
{
    char * res;
    char c;

    /* read each character from the result buffer */
    if (repeat) 
    {
        res = lastLine;
    } else {
        res = (char *)verRead(NULL);
        lastLine = res;
    }

    /* start a text message */
    if (THPLStartTextMsg() != 0)
    {
        return;
    }

    if (res)
    {
        while ((c = *res))
        {
            /* sent read character */
            if (THPLPutCharToMsg(c) != 0)
            {
                return;
            }
            res++;
        }

        /* send end of line */		   
        if (THPLPutCharToMsg('\n') != 0)
        {
            return;
        }
        /* finish the text message */   
        THPLFinishTextMsg();				 
    }
    else
    {
        if (THCLPutChar(0x02, IO_TIMEOUT) != THPL_OK)
        {
            return;
        }
    }

}

   
static void ContextSwitch(void *param1, void *param2)
{

    ;    
}
   
static void CacheTextUpdate(void * adrs, size_t bytes)
{
    ;
}
   
static void SetCoverageParams(void * covAddr, unsigned int partNo)
{
    ;
}

static void ResetAll(void *param1, void *param2)
{
    hardReset();
}

static void SetTimeout(int timeout, void *param2)
{      
    //testTimeout = timeout; 
}

   static void printOsVer()
   {
    // printf ("\n\n");
 
   }

static void SetRunAddr(UINT32 partId, void * addr)
 {
     testProgram = addr;
 }

static void BeforeTestLoadCmd(void *param1, void *param2)
{   	  
    /* call user routine */
    verBeforeTestLoad(param1, param2);
    /* send acknowladge message */
    THPLSendAckMsg(THPL_OK);     
}

static void SetTestParams(UINT32 p1, UINT32 p2)
{
    testParam1 = p1;
    testParam2 = p2;
}

static void getTestParams(int *p1, int *p2)
{
    *p1 = testParam1;
    *p2 = testParam2;
}

int getTestMode() 
{
    return testMode;
}

void testTask()
{
    OS_ERR os_err;
    while(1)
    {
        if(testReadyToRun && testProgram)
        {
            int param1, param2;
            getTestParams(&param1, &param2);
			tmBeforeTestRunHook(param1, param2);
            testProgram();
        }
        OSTimeDly(TEST_TASK_DELAY, OS_OPT_TIME_DLY, &os_err);
    }
}

void finishTestProgram()
{
    int param1, param2;
    getTestParams(&param1, &param2);
    tmAfterTestRunHook(param1, param2);
    currSummary = 0;
}

int testTaskStart()
{
    OS_ERR err;
    OSTaskCreate(   &testTask_TCB,
                    (CPU_CHAR    *)"testStart",
                    (OS_TASK_PTR )testTask,
                    (void	   * )0u,
                    (OS_PRIO     )TEST_TASK_PRIORITY,
                    &testTask_STK[0u],
                    TEST_TASK_STK_SIZE / 10u,
                    TEST_TASK_STK_SIZE,
                    (OS_MSG_QTY	 )0u,
                    (OS_TICK 	 )0u,
                    (void	    *)0u,
                    (OS_OPT		 )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR),
                    (OS_ERR	    *)&err);
    if (err != OS_ERR_NONE) 
    {
        return 1;
    }

    return 0;

}

int THPLTaskStart(void)
{
    OS_ERR err;
    OSTaskCreate(   &THPLTask_TCB,
                    (CPU_CHAR    *)"THPLStart",
                    (OS_TASK_PTR )THPLStart,
                    (void	   * )0u,
                    (OS_PRIO     )THPL_TASK_PRIORITY,
                    &THPLTask_STK[0u],
                    THPL_TASK_STK_SIZE / 10u,
                    THPL_TASK_STK_SIZE,
                    (OS_MSG_QTY	 )5u,
                    (OS_TICK 	 )0u,
                    (void	    *)0u,
                    (OS_OPT		 )(OS_OPT_TASK_STK_CHK | OS_OPT_TASK_STK_CLR),
                    (OS_ERR	    *)&err);
    if (err != OS_ERR_NONE) 
    {
        return 1;
    }

    return 0;
}

int targetAgentInit()
{
    ResetTestProgram();
    verInitStubTable();

    if (verBufOutputInit(resultBuf, resultBufLen) != VER_OK)
    {
        return 1;
    }
	  
    //if (testTaskStart != 0)
    //{
    //   return 2;
    //}
   
    /* initialize the test harness protocol */
    if (THPLInit(THPL_IO_TIME_OUT) != THPL_OK)
    {	     
        return 3;
    }     
   
    /* install default commands */
    if (THPLInstallCmd(RUN_TEST_CMD, (cmdFn_t)RunTest) != 0 ||
        THPLInstallCmd(REPORT_CMD, (cmdFn_t)Report) != 0 ||
        THPLInstallCmd(CTX_SWITCH_CMD, (cmdFn_t)ContextSwitch) != 0 ||
        THPLInstallCmd(CACHE_UPDATE_CMD, (cmdFn_t)CacheTextUpdate) != 0 ||
        THPLInstallCmd(SET_PARAMS_CMD, (cmdFn_t)SetTestParams) != 0 ||
        THPLInstallCmd(RESET_CMD, (cmdFn_t)ResetAll) != 0 ||
        THPLInstallCmd(SET_TIMEOUT_CMD, (cmdFn_t)SetTimeout) != 0 ||
        THPLInstallCmd(BEFORE_TEST_LOAD_CMD, (cmdFn_t)BeforeTestLoadCmd) != 0 ||
        THPLInstallCmd(SET_RUN_ADDR_CMD, (cmdFn_t)SetRunAddr) != 0)  
   {
        return 4;
   }

    return THPLTaskStart();

}

   

