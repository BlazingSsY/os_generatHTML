/* verotrg.h - Verocel Test Report Generator support library */

/* Copyright 2000-2007 Verocel, Inc. */

/*
modification history
--------------------
02l,07dec07,vjw Added support coverage only one partition
02k,08mar07,vjw Increased TH memory region
02i,22nov06,vti New implementation of memory access callbacks for PPC85xx
02k,26oct06,vjw Added uninstallStub, adapted for DMGS and OXF test harnesses
02j,02mar06,vjw More stubs
02i,29sep05,vjw Added remap mechanism
02h,08jul05,vjw Added verSetSpyAddr()
02h,24jun05,vjw Added memory spy
02g,11may05,vjw Removed SYSCALL_VER_GET_REAL_ADDR syscall
02f,04mar05,vjw Added macro VER_GET_TEST_PARTITION_NAME (for VThreads tests)
02e,06dec04,vjw Added macro VER_GET_TEST_PARTITION
02d,13sep04,vjw Added verBcmp
02c,23jun04,vti Added SymTabEntry struct
02b,18mar04,vti Updated according to STP
02a,10may03,vti Preliminary version based on previous projects
*/


#ifndef VEROTRG_H
#define VEROTRG_H

#include "typedefs.h"

#define  EOS '\0'
#define   UINT32  unsigned int
#define   INT32   int

#define VER_ERROR   1
#define VER_OK   0 	
#define STATUS   int 
#define UINT16   unsigned short 
#define INT16   unsigned short 		
//typedef signed short int INT16;
#define TRUE 1    // ����TRUEΪ1
#define FALSE 0   // ����FALSEΪ0
#define BOOL   int
#define VER_STATUS uint32_t

/*******task stk size and prio level************/
#define TASK_STK_SIZE64    64u
#define TASK_STK_SIZE128   128u
#define TASK_STK_SIZE256   256u
#define TASK_STK_SIZE2048  2048u
#define TASK_PRIO_3        3u
#define TASK_PRIO_4        4u
#define TASK_PRIO_5        5u
#define TASK_PRIO_6        6u
#define TASK_PRIO_7        7u
#define TASK_PRIO_8        8u
#define TASK_PRIO_9        9u
#define TASK_PRIO_10       10u
#define TASK_PRIO_11       11u
#define TASK_PRIO_12       12u
#define TASK_PRIO_13       13u
#define TASK_PRIO_14       14u
#define TASK_PRIO_15       15u
#define TASK_PRIO_16       16u
#define TASK_PRIO_17       17u
#define TASK_PRIO_18       18u



/********************MSG buffer, MAKER, MSG IE LENGTH ***********************************/
#define VER_MSG_MAX_LEN              1024      /* maximum size of a single message, must be less than half of buffer size */
#define VER_WRITE_MARKER             ('W')     /* reader: Wait, writer: can Write*/
#define VER_READ_MARKER              ('R')     /* reader: Read */
#define VER_BACK_MARKER              ('B')     /* reader: Back and read */
#define VER_OVERRUN_MARKER           ('O')     /* writer: can't Write*/
#define VER_MAX_EXPECTED_LENGTH      200       /* max length of expected value */
#define VER_MAX_ACTUAL_LENGTH        2*VER_MAX_EXPECTED_LENGTH        /* max length of actual value */
#define VER_MAX_COMMENT_LENGTH       64

#define DEBUG_VERSION


/*******  stubs parameter and variable*********/ 
#define NULL_ENTRY (0) // �յ�ַ
#define MAX_STUBS 10 // ����10׮
typedef void (*FUNCPTR)();
typedef struct {
    void *  original;  // ԭʼ������ַ
    void *  stub;      // ׮������ַ
    uint32_t oriCode;
} StubEntry;

extern StubEntry stubTable[MAX_STUBS + 1];

typedef struct {
    FUNCPTR  target;
    FUNCPTR  custHookFunc;
    uint32_t asm_tramp_addr;
    uint32_t insertFuncAddr;
    uint32_t oriCode;
} InsertStubEntry;

extern InsertStubEntry insertStubTable[MAX_STUBS + 1];

/*******  spy parameter *********/ 
//#define SPY_RD 0x00080000
//#define SPY_WR 0x00040000
//#define SPY_RDWR 0x000C0000
#define SPY_WR                              (0x01)
#define SPY_RD                              (0x02)
#define SPY_RDWR                            (0x03)

typedef void (*SPY_RTN)(int, void*);

		
#define VER_DEBUG(x,args...) \
     verFormatString(verDebugString,159,x, ## args),verComment(verDebugString);

#define DBGI(i)   (verComment (verItoa ((int)  (i))))
#define DBGL(l)   (verComment (verLtoa ((long) (l))))
#define DBGLL(ll)   (printf ("%lli\n",(long long) ll))
#define DBGX(x)   (verComment (verXtoa ((int)  (x))))

#define itoa verItoa
#define ltoa verLtoa
#define ftoa verFtoa
#define dtoa verDtoa
#define xtoa verXtoa


typedef enum {
    CPU_CRT_ENTER,
    CPU_CRT_EXIT,
    CPU_CRT_MAX
} CPU_CRT_STATE;


#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/* function declarations - Test API */
extern void   verHeader (char *testname, char *source, char *module, char *reqs, int maxTestCases);
extern void   verSummary (void);
extern void   verReqNum (char *reqNum);
extern void   verTestCase (int caseNumber);
extern void   verExpected (char *expectedValue);
extern void   verActual (char *actualValue);
extern void   verComment (char *str);
extern void   verPassed (int caseNumber);
extern void   verFailed (int caseNumber);
extern int    verCheck    (int checkno, int condition);
extern void   verCheckDead      (void);
extern void   verTestCaseStatus (int caseNumber);
extern void   verWrite (char *msg);
extern int    verRead (char* buff);
extern int    verStrcpy (char *dest, const char *src);
extern int    verStrcat (char *dest, const char *append);
extern int    verStrcmp (char *s1, char *s2);
extern int    verStrlen (char * s);
extern char * verStrncpy (char *dest, const char *src, int n);
extern char * verItoa (int value);
extern char * verLtoa (long value);
extern char * verFtoa (float value, unsigned int ndec);
extern char * verDtoa (double value, unsigned int ndec);
extern char * verXtoa (int value);
extern char * verFormatString (char *buff, int maxLength, const char *format, ... );
extern int    verBcmp (char *buf1, char *buf2, int nbytes);
extern void * verMemcpy(void * destination, const void * source, int size);
extern void * verMemset(void * m, char c, int size);


extern CPU_CRT_STATE checkCrtState (void);

#ifdef DEBUG_VERSION
extern void verFlush ();
#endif

/************************stub api*******************/
uint32_t verInstallStub(void *  oriAddr, void * jumpAddr, uint32_t StubType);
uint32_t verUninstallStub(void *  oriAddr, uint32_t StubType);
VER_STATUS verUninstallAllStubs(uint32_t StubType);
VER_STATUS verInitStubTable(void);
//uint32_t verGetRealAddr(FUNCPTR stubbed);
uint32_t installStub(uint32_t addr, uint32_t jump, uint32_t StubType);
uint32_t uninstallStub(uint32_t addr, uint32_t StubType);
//void callFunction(FUNCPTR original);

/************************spy api*******************/
VER_STATUS verInstallSpy(int mode, void *addr, SPY_RTN fn);
VER_STATUS verUninstallSpy(void);
VER_STATUS verSetSpyAddr (int mode, void *addr);
extern void _verSpyEnable(int mode, void* address);
extern void _verSpyDisable(void);

void IVOR15Handler_Spy(void);



/* test harness internals */
extern int verBufOutputInit(char * buf, int len);
extern void   verFlush ();
extern int targetAgentInit();
extern void finishTestProgram();


#ifdef __cplusplus
}
#endif /* __cplusplus */


#endif	/* VEROTRG_H */


