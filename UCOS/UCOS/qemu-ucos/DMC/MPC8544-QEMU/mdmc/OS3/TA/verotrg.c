/* verotrg.c - Verocel Test Support library */

/* Copyright 2000-2012 Verocel, Inc. */

/*
modification history
--------------------
03m,10aug12,vjw Added check for valid mode in verInstallSpy/verSetSpyAddr
03l,28jun12,vjw Introduced soft float support and removed status for verHeader
03k,10may11,vjw Added additional checks to avoid use two test styles
                in one test case
03j,23mar11,vjw Discarded the last fix of PR115
03i,23mar11,vjw Fixed: PR:115 verGetRealAddr may return invalid address
03h,21mar11,vjw Fixed mailboxes to support send of 0 value
03f,08apr08,vjw Stop coverage before partition restarting
03e,22jan08,vjw Fixed comments
03d,11dec07,vjw Added partiton names table
03c,07dec07,vjw Added support coverage only one partition
03b,22nov06,vti New implementation of memory access callbacks for PPC85xx
03a,03nov06,vjw Adapted to new TH
02r,26oct06,vjw Added uninstallStub 
02p,13oct06,vjw Mearged with SCOE TH
02o,25apr06,tle Added verStartTestSetDirect and verStartTestDirectWithCoverage
                to support no memory allocation from CoreOS
02n,06oct05,tle Added global verReadEx and local verGetMsgLength functions
02m,24jun05,vjw Added memory spy
02l,11may05,vjw Modified verGetRealAddr function (removed use of ltTable)
02k,04mar05,vjw Added partition names table (for vThreads tests)
02j,02mar05,tle Fixed warning messages
02i,21dec04,tle Modified verDumpCoverageTable function to VerOCode API
02i,20dec04,vti Fixed bug in verWriteEx
02h,16nov04,vti New implementation of the ring buffer (dynamic message size)
02g,15nov04,vti Added verCheck and related support (per partition)
02f,13sep04,vjw Added verBcmp
02e,31mar04,vti Added verStartTestSetByIdxWithCoverage() wrapper.
02d,25mar04,vti Modified verRead(), added starting test set by index
02c,17mar04,vti Updated according to STP
                Added interpartition sychronization
02b,19sep03,vti First complete mv5100 target version
02a,10may03,vti Preliminary version for simulator based on previous projects
*/

/*
DESCRIPTION
This file provides the standard test report I/O routines, as weel as
convenient APIs used to generate the test reports to be sent on the host.
The result is tagged for easy XML conversion on on the host.

This module also provides common set of test support rotuines for stubs,
coverage monitor, etc.

Example of test procedure with two convetions of writting test case:
- convention 1: using verExpected()/verCheck()/verTestCaseStatus()
- convention 2: using verExpected()/verActual()/verTestCaseStatus()



INTERNAL
The 'tags' are made of one character placed before the information.
Thus, a line output looks like "T 1" where 'T' is the tag and '1' is the data.
A 'N' stands for "test case number"
   R  - requirement number(s)
   E  - expected value
   A  - actual value
   C  - comment
   S  - status (value is either PASS or FAIL)

   P  - test procedure name
   L  - library (file) under test
   F  - function under test
   Q  - requirement number(s) listed in verHeader
   M  - max test cases

   !  - test harness internal error message


The following tags are used for coverage information :
   H  - header record
   T  - trailer record
   Z  - Z block record
   D  - D block record
   +  - D block subsequent lines
   X  - X block record

The "I/O" mechanism is a ring buffer. Outgoing messages are sent to the buffer
using the verWrite() API. The host driver may use the verRead() function to fetch
the messages.

INCLUDE FILES

*/

/* includes  */
#include "verotrg.h"
#include "math.h"
#include "stdarg.h"        /* va-arg stuff */
#include "string.h"
#include "typedefs.h"
#include "time.h"
#include "cpu.h"
#include "os.h"


/* defines */
#define to_char(n)  ((char)((n) + '0'))
#define MAX_DIGIT   (80)   /* max digits */
#define VER_ABS(n)  (((n)<0)?(-(n)):(n))


/* globals */
static char *      veroBuf        =    (char *)0;
static int         veroBufLen       =    0;
char *             veroBufRdPtr    =    (char *)0;
char *             veroBufWrPtr    =    (char *)0;
static char        verExpStr[VER_MAX_EXPECTED_LENGTH];
static char        verActStr[VER_MAX_ACTUAL_LENGTH];
static int         verExpStrLen;
static int         verActStrIdx;
static int         verActualCalled;
static int         verCheckCalled;
static int         verActualCaseNumber;
static char *      fillString = "Verocel";

/*globals for stub*/
uint32_t stubCount = 0; // it is stub number, and stubTable index
StubEntry stubTable[MAX_STUBS + 1];

/*globals for spy */
SPY_RTN 	verSpyHookAddr = NULL;
BOOL		verFlashStub = 0;	

/*globals for check system*/
uint32_t sysStatus;

/* forward declarations */
static void shortTag (char tag, char *tagValue);
void verWrite (char *msgText);
void verCheckSysStatus (void);
void writeSysStatusComment(void);

/************function for insert stub****************/
/*trampoline function*/
extern void asm_trampoline_slotA(void);
extern void asm_trampoline_slotB(void);
extern void asm_trampoline_slotC(void);
extern void asm_trampoline_slotD(void);
extern void asm_trampoline_slotE(void);
extern void asm_trampoline_slotF(void);
extern void asm_trampoline_slotG(void);
extern void asm_trampoline_slotH(void);
extern void asm_trampoline_slotI(void);
extern void asm_trampoline_slotJ(void);
/*asm_insert function*/
extern void InsertFunC_A(void);
extern void InsertFunC_B(void);
extern void InsertFunC_C(void);
extern void InsertFunC_D(void);
extern void InsertFunC_E(void);
extern void InsertFunC_F(void);
extern void InsertFunC_G(void);
extern void InsertFunC_H(void);
extern void InsertFunC_I(void);
extern void InsertFunC_J(void);
/*customer function will be called in asm_insert function*/
 void custFunctionA(void);
 void custFunctionB(void);
 void custFunctionC(void);
 void custFunctionD(void);
 void custFunctionE(void);
 void custFunctionF(void);
 void custFunctionG(void);
 void custFunctionH(void);
 void custFunctionI(void);
 void custFunctionJ(void);

 InsertStubEntry insertStubTable[MAX_STUBS + 1];
 uint32_t insertStubCount = 0;

void custFunctionA(void)
 {
    if(insertStubTable[0].custHookFunc != NULL_ENTRY)
        insertStubTable[0].custHookFunc();
 }

 void custFunctionB(void)
 {
    if(insertStubTable[1].custHookFunc != NULL_ENTRY)
        insertStubTable[1].custHookFunc();
 }

 void custFunctionC(void)
 {
    if(insertStubTable[2].custHookFunc != NULL_ENTRY)
        insertStubTable[2].custHookFunc();
 }

 void custFunctionD(void)
 {
    if(insertStubTable[3].custHookFunc != NULL_ENTRY)
        insertStubTable[3].custHookFunc();
 }

 void custFunctionE(void)
 {
    if(insertStubTable[4].custHookFunc != NULL_ENTRY)
        insertStubTable[4].custHookFunc();
 }

 void custFunctionF(void)
 {
    if(insertStubTable[5].custHookFunc != NULL_ENTRY)
        insertStubTable[5].custHookFunc();
 }

 void custFunctionG(void)
 {
    if(insertStubTable[6].custHookFunc != NULL_ENTRY)
        insertStubTable[6].custHookFunc();
 }

 void custFunctionH(void)
 {
    if(insertStubTable[7].custHookFunc != NULL_ENTRY)
        insertStubTable[7].custHookFunc();
 }

 void custFunctionI(void)
 {
    if(insertStubTable[8].custHookFunc != NULL_ENTRY)
        insertStubTable[8].custHookFunc();
 }

 void custFunctionJ(void)
 {
    if(insertStubTable[9].custHookFunc != NULL_ENTRY)
        insertStubTable[9].custHookFunc();
 }

/*************************************************************************
*
* verHeader - write information about test procedure 
*
* This function must be called by a test procedure before any
* further actions are performed.
*
* RETURNS: N/A
*
* ERRNO: N/A
*/
void verHeader
   (
   char   *testname,    /* functional test name */
   char   *source,      /* source file */
   char   *module,      /* module under test */
   char   *reqs,        /* requirements verified */
   int     maxTestCases   /* total number of test cases */
   )
{
    verCheckSysStatus();
    shortTag ('P', testname);
    shortTag ('L', source);
    shortTag ('F', module);
    shortTag ('Q', reqs);
    shortTag ('M', verItoa(maxTestCases));
}

/*************************************************************************
*
* verSummary - exit from a test procedure
*
* This function must be called at the exit of a test procedure.
*
* RETURNS: N/A
*
* ERRNO: N/A
*/
void verSummary (void)
{
    finishTestProgram();
}

/*************************************************************************
*
* verReqNum - write a list of requirements for current test case
*
* This function should be called in each test case.
*
* RETURNS: N/A
*
* ERRNO: N/A
*
* SEE ALSO:
* verTestCase()
*/
void verReqNum(char *reqNum)
{
    shortTag ('R', reqNum);
}

/*************************************************************************
*
* verComment - write a comment tag
*
* RETURNS: N/A
*
* ERRNO: N/A
*
*/
void verComment(char *str)
{
    shortTag ('C', str);
}


/*************************************************************************
*
* verTestCase - start new test case
*
* Since a new test case begins, previous expected and actual values are
* also reset. 
*
* RETURNS: N/A
*
* ERRNO: N/A
*
* SEE ALSO:
* verExpected(), verActual()
*
*/
void verTestCase(int caseNumber)
{
    int i;
    verActualCaseNumber = caseNumber;
    shortTag ('N', verItoa(caseNumber));
    /* clear buffer for the expected value */
    verExpStrLen = 0;
    for (i=0;i<(sizeof(verExpStr)/sizeof(char));i++) {
        verExpStr[i] = '\0';
    }
    /* clear buffer for the actual value */
    verActStrIdx = 0;
    for (i=0;i<(sizeof(verActStr)/sizeof(char));i++) {
        verActStr[i] = '\0';
    }
    /* reset flags */
    verActualCalled = 0;
    verCheckCalled  = 0;
}

/*************************************************************************
*
* verPassed - finish test case with pass status
*
* This subroutine checks if the caseNumber is the same as passed to
* routine verTestCase(). If they match then write a PASS status,
* otherwise FAIL status.
*
* RETURNS: N/A
*
* ERRNO: N/A
*/
void verPassed (int caseNumber)
{
    if (verCheckCalled) {
        verComment("Error: Cannot use verCheck() together with verPassed()!");
        verFailed(caseNumber);
        return;
    }

    if (!verActualCalled) {
        verComment("Error: Call verActual() before verPassed()!");
        verFailed(caseNumber);
        return;
    }

    if (sysStatus != 0)
    {
        writeSysStatusComment();
        shortTag ('S', "FAIL");
        return;
    }
         	
   	if (caseNumber == verActualCaseNumber) 
   	{
        shortTag ('S', "PASS");
    }
    else
    {
        verComment("Error: Case numbers from verTestCase()/verPassed()"
      	           " don't match!");
        verFailed(caseNumber);
    }
}

/*************************************************************************
*
* verFailed - finish test case with fail status
*
* This subroutine writes status (FAIL) for current test case.
*
* RETURNS: N/A
*
*/
void verFailed (int caseNumber)
{
    shortTag ('S', "FAIL");
}

/*************************************************************************
* verExpected - set expected result string
*
* This subroutine writes the expected string for the current test case.
* It should be called after verTestCase().
*
* RETURNS: N/A
*
* ERRNO: N/A
*
*/
void verExpected (char *str)
{
    shortTag ('E', str);
    /* save the expected value */
    verStrncpy(verExpStr,str,VER_MAX_EXPECTED_LENGTH);
    /* force null-terminated string */
    verExpStr[VER_MAX_EXPECTED_LENGTH-1] = '\0';
    verExpStrLen = verStrlen(verExpStr);
}

/*************************************************************************
*
* verActual - set actual result string
*
* This subroutine writes the actual string for the current test case.
* It should be called after verTestCase() and verExpected().
*
* RETURNS: N/A
*
* ERRNO: N/A
*
*/
void verActual (char *str )
{
    verActualCalled = 1;
    shortTag ('A', str);
    /* save the actual value - it may be an error situation
    where it overwrite the results of previous callse to verCheck()
    however we will detect this in a call to verTestCaseStatus()
    */
    verStrncpy(verActStr,str,VER_MAX_ACTUAL_LENGTH);
    /* force null-terminated string */
    verActStr[VER_MAX_ACTUAL_LENGTH-1] = '\0';
}

/*************************************************************************
*
* verCheck - append actual string tag according to the condition.
*
* This function appends actual string with a character at position <checkno>
* of the expected string (see verExpected()) and when the condition
* is false with an extra dash. If <checkno> is greater than size of expected
* string then an asterisk is used. Indexes start with 1.
*
* RETURNS: value of the condition
*
* ERRNO: N/A
*
*/
int verCheck (int checkno, int condition)
{
    verCheckCalled = 1;
    if (verActStrIdx<VER_MAX_ACTUAL_LENGTH-1) {
        verActStr[verActStrIdx++] =
            ((checkno > verExpStrLen || checkno<1) ? '*' : verExpStr[checkno-1]);
        if (!condition) {
            verActStr[verActStrIdx++] = '-';
        }
    }
    return (condition);
}


/*************************************************************************
*
* verCheckDead - append actual string tag with '!'.
*
* This function appends verActStr with '!', meaning that code that
* should not execute was executed.
*
* RETURNS: N/A
*
* ERRNO: N/A
*
*/
void verCheckDead (void)
{
    verCheckCalled = 1;
    if (verActStrIdx<VER_MAX_ACTUAL_LENGTH) {
        verActStr[verActStrIdx++] = '!';
    }
}

/*************************************************************************
*
* verTestCaseStatus - write the test case status message
*
* \is
* \i This subroutine writes status (FAIL) for current test case if:
* \i - verCheck() and verActual() was called in one test case or
* \i - neither verCheck() nor verActual() was called in test case or
* \i - actual sting doesn't match expected string
* \ie
* Otherwise it writes status (PASS). Addtionaly it writes actual string 
* if verActual() wasn't called in current test case.
*
*
* RETURNS: N/A
*
* ERRNO: N/A
*/
void verTestCaseStatus (int caseNumber)
{
    /* test case is not allowed to call both verCheck and verActual */
    if (verCheckCalled && verActualCalled) {
        verComment("Error: Both verCheck() and verActual() called!");
        verFailed(caseNumber);
        return;
    }
    /* test case must call to one of verCheck or verActual */
    if (!verCheckCalled && !verActualCalled) {
        verComment("Error: Neither verCheck() nor verActual() called!");
        verFailed(caseNumber);
        return;
    }
    /* if verActual was not called directly call it now */
    if (!verActualCalled) {
        verActual(verActStr);
    }
    /* determine the test case status */
    if (verStrcmp(verExpStr,verActStr)==0) {
        if (caseNumber == verActualCaseNumber) 
        {
            if (sysStatus != 0)
            {
                writeSysStatusComment();
                shortTag ('S', "FAIL");
                return;
            }
            shortTag ('S', "PASS");
        }
        else
        {
            verComment("Error: Case numbers from verTestCase()/verTestCaseStatus()"
                     " don't match!");
            verFailed(caseNumber);
        }
    }
    else {
        verFailed(caseNumber);
    }
}


/*************************************************************************
*
* shortTag - Format a string with a tag and a value. Send it to the host
*
* RETURNS: N/A
*
* NOMANUAL
*/
void shortTag(char tag, char *value)
{
    char formTag[VER_MSG_MAX_LEN+2];
    /* carve start of message */
    formTag[0] = tag;
    formTag[1] = ' ';
    verStrncpy(&formTag[2],value,VER_MSG_MAX_LEN);
    /* ensure msg is always null-terminated */
    formTag[VER_MSG_MAX_LEN+1] = '\0';
    verWrite(formTag);
}


/*******************************************************************************
*
* verBufOutputInit - initializes buffer for output
*
* This routine initialize buffer for output.
*
* RETURNS: VER_ERROR on error, VER_OK on success
*
* ERRNO: N/A
*/
int verBufOutputInit(char * buf, int len)
{
    int i;
    if (len > VER_MSG_MAX_LEN * 2)
    {	
        veroBuf = buf;
        for (i = 0; i < len; i++)
        {
            veroBuf[i] = VER_WRITE_MARKER;
        }
        veroBufLen = len;
        veroBufRdPtr = veroBuf;
        veroBufWrPtr = veroBuf;
        return  VER_OK;
    } else {
        return  VER_ERROR;
    }
}
   
/*************************************************************************
*
* verWrite - put a new message to the buffer, extended
*
* This subroutine writes a message into the buffer if space is available.
* If the buffer becomes full, this routine will overwrite the oldest message
* with an error message.
*
* RETURNS: N/A
*
* NOMANUAL
*/
void verWrite (char *msgText)
{

    int ilevel;
    char *wrptr;
    int overruncond;
    int msgLen;

    /* truncate string if it is too long */
    msgLen = verStrlen(msgText);
    if (msgLen > VER_MSG_MAX_LEN+1) {
        /* message too long - truncate */
        msgLen = VER_MSG_MAX_LEN+1;
        msgText[VER_MSG_MAX_LEN+1] = '\0';
    }

    //ilevel = intLock();

    if (*veroBufWrPtr==VER_WRITE_MARKER) {
        /* how much room do we need: pd_idx + space + msg + EOS + marker */
        msgLen = 3+msgLen+2;

        /* how much room do we have to the end of buffer */
        if (veroBufWrPtr + msgLen <  veroBuf + veroBufLen) {
            /* still enough room */
            *veroBufWrPtr = VER_READ_MARKER;
            wrptr = veroBufWrPtr+1;
            /* check for overrun */
            overruncond = (veroBufWrPtr < veroBufRdPtr) &&
                          (veroBufRdPtr <= veroBufWrPtr+msgLen);
        }
        else {
            /* need to rewind */
            *veroBufWrPtr = VER_BACK_MARKER;
            wrptr = veroBuf;
            /* check for overrun */
            overruncond = (veroBufWrPtr < veroBufRdPtr) ||
                          (veroBufRdPtr <= veroBuf+msgLen);
        }

        if (overruncond) {
            /* if we detected an overrun then we only change the marker */
            *veroBufWrPtr = VER_OVERRUN_MARKER;
        }
        else {
            /* we can put the message now */
            wrptr[0] =  '0';
            wrptr[1] =  '0';
            wrptr[2] = ' ';
            verStrcpy(&wrptr[3],msgText);
            wrptr[msgLen-1] = VER_WRITE_MARKER;
            /* and adjust the write pointer */
            veroBufWrPtr = &wrptr[msgLen-1];
        }
    }
   // intUnlock(ilevel);
}


/*************************************************************************
*
* verWriteUserData - puts user data to the resul buffer
*
* This subroutine writes a message into the buffer with X tag.
*
* RETURNS: N/A
*
* NOMANUAL
*/
void verWriteUserData (char *msgText)
{   
    shortTag ('X', msgText);
}

/*************************************************************************
*
* verRead - get messages from the buffer
*
* This subroutine gets message from the buffer if it is available.
*
* RETURNS: address of the message
*
* NOMANUAL
*/
int verRead (char* buff)
{

    static char *OVERRUNMSG = "00 ! RESULTS BUFFER OVERRUN ERROR !!!";
    int addr = 0;
    char *rdptr;
    int ilevel;

    // ilevel = intLock();

    switch (*veroBufRdPtr) {
        case VER_OVERRUN_MARKER:
            rdptr = OVERRUNMSG;
            break;
        case VER_READ_MARKER:
            rdptr = veroBufRdPtr+1;
            break;
        case VER_BACK_MARKER:
            rdptr = veroBuf;
            break;
        case VER_WRITE_MARKER:
        default:
            rdptr = NULL;
    }

    if (rdptr) {
        if (buff) {
            verStrcpy(buff, rdptr);
            addr = (int)buff;
        }
        else {
            addr = (int)rdptr;
        }
        /* adjust the read pointer */
        if (*veroBufRdPtr!=VER_OVERRUN_MARKER) {
            veroBufRdPtr = rdptr + verStrlen(rdptr) + 1;
        }
        else {
            /* we sent error message, so we can unlock writer */
            *veroBufRdPtr = VER_WRITE_MARKER;
        }
    }

    // intUnlock(ilevel);

    return addr;

}

#ifdef DEBUG_VERSION
//#include "stdio.h"
/*************************************************************************
*
* verFlush - flushes out any results on console
* NOMANUAL
*/


void verFlush ()
{
    char tmpMsg[VER_MSG_MAX_LEN];
    verMemset((void *)tmpMsg, '\0', VER_MSG_MAX_LEN);
    while(verRead(tmpMsg)) {
    //    printf("%s\n",tmpMsg);
    ;
    }
}

#endif


/***************************************************************************
* cert_cvt - This subroutine converts a number to string.
*
* RETURNS: a string presents a number.
* NOMANUAL
*/
char *cert_cvt(char *strCvt, long value)
{
    BOOL   dosign  = FALSE;   /* positive=false, negative=true */
    long   n;                  /* temporary value */
    char   *save = strCvt;

    /* check for nagative value */
    if (value < 0) {
        dosign = TRUE;
    }

    /* start the integral conversion */
    n = (long) value;
    do {            /* get the length */
        strCvt++;
    } while (n /= 10);

    if (dosign) strCvt++;

    *strCvt = '\0';

    n = (long) value;
    do {
        *--strCvt = to_char (VER_ABS(n % 10));
    } while (n /= 10);

    if (dosign) *(--strCvt) = '-';

    return (save);
}

/***************************************************************************
* cert_cvtf - This subroutine converts a float number to string.
*
* RETURNS: a string presents a number.
* NOMANUAL
*/
char *cert_cvtf(char *strCvt, double value, unsigned int ndec)
{
    BOOL     dosign  = FALSE;   /* positive=false, negative=true */
    long     ipart;   /* integral parts */
	double   fpart;   /* factional parts */
    double   tmp;     /* temporary value */
    char    *save = strCvt;

    /* check for nagative value */
    if (value < 0) {
        value = -value;
        dosign = TRUE;
    }

    ipart = (long)value;
	fpart = value - ipart;
    if (dosign) 
	{
	    *(strCvt++) = '-';
    }

    strCvt = cert_cvt(strCvt, ipart);
  
    if (!ndec)
    {
        return (save);
    }

    /* start the fractional conversion */
    while (*strCvt++ != EOS)
        ;

    *(strCvt-1) = '.';   /* replace the EOS with '.' */

    do {
	    tmp = fpart * 10;
        ipart = (long)tmp;
		fpart = tmp - ipart;
        *strCvt++ = to_char (ipart % 10);
    } while (--ndec);

    *strCvt = EOS;

    return (save);
}

/***************************************************************************
* verItoa - convert integer to string
*
* RETURNS: number coverted to string
*
* ERRNO: N/A
*/
char *verItoa(int value)
{
    static char strCvt[MAX_DIGIT];
    return cert_cvt (strCvt, value);
}
   
/***************************************************************************
* verLtoa - convert long integer to string
*
* RETURNS: number coverted to string
*
* ERRNO: N/A
*/
char *verLtoa(long value)
{
    static char strCvt[MAX_DIGIT];
    return cert_cvt (strCvt, value);
}

/***************************************************************************
* verFtoa - convert float to string
*
* RETURNS: number coverted to string
*
* ERRNO: N/A
*/
char *verFtoa(float    value, unsigned int ndec)
{
    static char strCvt[MAX_DIGIT];
    strCvt[MAX_DIGIT-1]='\0';
    return cert_cvtf (strCvt, value * 1.0, ndec);
}

/**************************************************************************
* verDtoa - convert double to string
*
* RETURNS: number coverted to string
*
* ERRNO: N/A
*/
char *verDtoa(double    value, unsigned int ndec)
{
    static char strCvt[MAX_DIGIT];
    return cert_cvtf (strCvt, value, ndec);
}


/*************************************************************************
* verXtoa - convert integer to hex. representation
*
* RETURNS: number coverted to string
*
* ERRNO: N/A
*/
char *verXtoa(int value)
{
    static char strHex[9];
    int i;
    for (i=0; i<8; i++) {
        switch ((value >> (4*i)) & 0x0000000F) {
            case 0 : strHex[7-i]='0';
                break;
            case 1 : strHex[7-i]='1';
                break;
            case 2 : strHex[7-i]='2';
                break;
            case 3 : strHex[7-i]='3';
                break;
            case 4 : strHex[7-i]='4';
                break;
            case 5 : strHex[7-i]='5';
                break;
            case 6 : strHex[7-i]='6';
                break;
            case 7 : strHex[7-i]='7';
                break;
            case 8 : strHex[7-i]='8';
                break;
            case 9 : strHex[7-i]='9';
                break;
            case 10: strHex[7-i]='a';
                break;
            case 11: strHex[7-i]='b';
                break;
            case 12: strHex[7-i]='c';
                break;
            case 13: strHex[7-i]='d';
                break;
            case 14: strHex[7-i]='e';
                break;
            case 15: strHex[7-i]='f';
                break;
            default: strHex[7-i]='X';
        }
    }
    strHex[8] = '\0';
    return strHex;
}


/*******************************************************************************
*
* verStrlen - compute length of a string (ANSI)
*
* This routine returns the number of characters in <s>, not including EOS.
*
* RETURNS: length of string.
*
* ERRNO: N/A
*/

int verStrlen(char * s)
{
    const char *save = s + 1;

    while (*s++ != EOS)
        ;

    return (s - save);
}

/*************************************************************************
*
* verStrcpy - copy a string
*
* This routine copies string <src> (including EOS) to string <dest>.
*
* RETURNS: a length of the resulted string.
*
* ERRNO: N/A
*/
int verStrcpy(char *dest, const char *src)
{
    char *save = dest;
    while ( (*dest++ = *src++) != EOS )
        ;

    return verStrlen(save);
}


/*******************************************************************************
*
* verStrncpy - copy n characters from one string to another (ANSI)
*
* This routine copies <n> characters from string <s2> to string <s1>.
* If <n> is greater than the length of <s2>, nulls are added to <s1>.
* If <n> is less than or equal to the length of <s2>, the target
* string will not be null-terminated.
* 
* RETURNS: A pointer to <s1>.
*
* ERRNO: N/A
*/

char *verStrncpy(char *      s1, const char *s2, int n)
{
    char *d = s1;

    if (n != 0) {
        while ((*d++ = *s2++) != 0) {
            if (--n == 0)
                return (s1);
        }

        while (--n > 0)
            *d++ = EOS;         /* NULL terminate string */
    }

    return (s1);
}

/*************************************************************************
*
* verStrcat - concatenate a string
*
* This routine appends a copy of string <append> to the end of string 
* <dest>.  The resulting string is null-terminated.
*
* RETURNS: a length of the resulted string.
*
* ERRNO: N/A
*/
int verStrcat(char *dest, const char *append)
{
    char *save = dest;

    while ( *dest++ != EOS )   /* find end of string */
        ;

    dest--;

    while ( (*dest++ = *append++) != EOS )
        ;

    return verStrlen(save);
}

/*******************************************************************************
*
* verStrcmp - compare two strings lexicographically (ANSI)
*
* This routine compares string <s1> to string <s2> lexicographically.
*
* RETURNS: An integer greater than, equal to, or less than 0,
* according to whether <s1> is lexicographically
* greater than, equal to, or less than <s2>, respectively.
*
* ERRNO: N/A
*/

int verStrcmp(char * s1, char * s2)
{
    while (*s1++ == *s2++)
        if (s1 [-1] == EOS)
            return (0);

    return ((s1 [-1]) - (s2 [-1]));
}


/*******************************************************************************
*
* verFill - fill buffer with data
*
* This routine fills buffer with pattern.
*
* RETURNS: N/A
*
* ERRNO: N/A
*/
void verFill(char *buf, int  nbytes, int baseIndex)
{
    int idx;
    int fillStrLen = verStrlen(fillString);

    for (idx=0; idx<nbytes; idx++) {
        *buf = baseIndex + (idx ^ fillString[idx % fillStrLen]);
        buf++;
    }

}

/*******************************************************************************
*
* verBcmp - compare one buffer to another
*
* This routine compares the first <nbytes> characters of <buf1> to <buf2>.
*
* RETURNS:
*   0 if the first <nbytes> of <buf1> and <buf2> are identical,
*   less than 0 if <buf1> is less than <buf2>, or
*   greater than 0 if <buf1> is greater than <buf2>.
*
* ERRNO: N/A
*/

int verBcmp( char *buf1, char *buf2, int nbytes)
{
    const unsigned char *p1;
    const unsigned char *p2;

    /* size of memory is zero */

    if (nbytes == 0)
        return (0);

    /* compare array 2 into array 1 */

    p1 = (const unsigned char *)buf1;
    p2 = (const unsigned char *)buf2;

    while (*p1++ == *p2++)
    {
        if (--nbytes == 0)
            return (0);
    }

    return ((*--p1) - (*--p2));
}

/*******************************************************************************
*
* verMemcpy - copy memory from one location to another
*
* This routine copies <size> characters from the object pointed
* to by <source> into the object pointed to by <destination>. If copying
* takes place between objects that overlap, the behavior is undefined.
*
* RETURNS: A pointer to <destination>.
*
* ERRNO: N/A
*/

void * verMemcpy(void * destination, const void * source, int size)
{
    char * dst = (char *)destination;
   	char * src = (char *)source;
    while (size--)
    {
        *((char *)dst) = *(char *)src;
        dst++;
        src++;
    }

    return (destination);
}

/*******************************************************************************
*
* verMemset - set a block of memory
*
* This routine stores <c> converted to an `unsigned char' in each of the
* elements of the array of `unsigned char' beginning at <m>, with size <size>.
*
* RETURNS: A pointer to <m>
*
* ERRNO: N/A
*/

void * verMemset(void * m, char c, int size)
{
    char * dst = (char *)m;
    while (size--)
    {
        *((char *)dst) = c;
        dst++;
    }

    return (m);
}

/*******************************************************************************
*
* verFormatString - form a string into a buffer
*
* This routine formes a string using a specified format string <format>.
* The following format tags are allowed:
*   %i   int*      (integer)
*   %l   long*     (long integer)
*   %f   float*    (float - 10 digits in fraction)
*   %d   double*   (double - 10 digits in fraction)
*   %s   char*     (string)
*   %c   char*     (single character)
*   %x   int*      (integer - 4 bytes - hexadecimal)
*
*  Extentions:
*   %f,%d  may be followed by a digit 0-9 that specifies number of decimal digits
*          in fraction part, e.g. %d3 for 345.12345 gives "345.123"
*
* IMPORTANT NOTE:
*   All values must be passed thru pointers!
*
* RETURNS: Pointer to <buff>.
*
* ERRNO: N/A
*/

char *verFormatString
(
    char *buff,
    int maxLength,
    const char *format,
    ...
)
{
    va_list ap;

    int formPos;
    int buffPos;
    int len;
    char *str;

    /* clear the buffer */
    for (buffPos=0; buffPos<maxLength; buff[buffPos++]=EOS);

    va_start(ap,format);

    formPos = 0;
    buffPos = 0;

    while (format[formPos] != EOS) {

        /* do not exceed allowed space */
        if (buffPos >= maxLength-1) {
            break;
        }

        if (format[formPos] == '%') {
            switch (format[formPos+1]) {
                case 'c':
                    buff[buffPos++] = *va_arg(ap,char*);
                    formPos += 2;
                    continue;
                case 'i':
                    str = verItoa(*va_arg(ap,int*));
                    break;
                case 'l':
                    str = verLtoa(*va_arg(ap,long*));
                    break;
                case 'x':
                    str = verXtoa(*va_arg(ap,int*));
                    break;
                case 'f':
                    len = format[formPos+2]-'0';
                    if (len>=0 && len<=9) {
                        str = verFtoa(va_arg(ap,double),len);
                        formPos++;
                    }
                    else {
                        str = verFtoa(va_arg(ap,double),10);
                    }
                    break;
                case 'd':
                    len = format[formPos+2]-'0';
                    if (len>=0 && len<=9) {
                        str = verDtoa(va_arg(ap,double),len);
                        formPos++;
                    }
                    else {
                        str = verDtoa(va_arg(ap,double),10);
                    }
                    break;
                case 's':
                    str = va_arg(ap,char*);
                    break;
                default:
                    buff[buffPos++] = format[formPos++];
                    continue;
            }
            len = verStrlen(str)+buffPos < maxLength ? verStrlen(str) : maxLength-buffPos-1;
            verStrncpy(buff+buffPos,str,len);
            buffPos += len;
            formPos += 2;
        }
        else {
            buff[buffPos++] = format[formPos++];
        }
    }

    va_end(ap);
    return buff;
}


/*******************************************************************************
*
*  fucntion for change text code
*/

void ppc_code_write(uint32_t paddr, uint32_t val)
{
    CPU_SR_ALLOC();
    CPU_CRITICAL_ENTER();
    *(volatile uint32_t *)paddr = val;
    __asm__ volatile("dcbf 0,%0; sync; icbi 0,%0; sync; isync" :: "r"(paddr));
    CPU_CRITICAL_EXIT();
}

void verFuncRedirect(uint32_t addr, uint32_t jump)
{

    uint32_t jumpCode = 0x48000000 | (((int32_t)jump - (int32_t)addr)& 0x03FFFFFC);
    /* 写桩 */
    CPU_SR_ALLOC();
    CPU_CRITICAL_ENTER();
    *(volatile uint32_t *)addr = jumpCode;
    __asm__ volatile("dcbf 0,%0; sync; icbi 0,%0; sync; isync" :: "r"(addr));
    CPU_CRITICAL_EXIT();
}

void verRecoverFunc(uint32_t addr, uint32_t oriCode)
{
    /* 写桩 */
    CPU_SR_ALLOC();
    CPU_CRITICAL_ENTER();
    *(volatile uint32_t *)addr = oriCode;
    __asm__ volatile("dcbf 0,%0; sync; icbi 0,%0; sync; isync" :: "r"(addr));
    CPU_CRITICAL_EXIT();
}

/*******************************************************************************
*
*  verInitStubTable - init both stub table
*
*/
VER_STATUS verInitStubTable(void) 
{
 
	for (int i = 0; i < MAX_STUBS; i++) 
    {
        stubTable[i].original = NULL_ENTRY;
		stubTable[i].stub = NULL_ENTRY;
        stubTable[i].oriCode = 0;
        insertStubTable[i].target = NULL_ENTRY;
		insertStubTable[i].custHookFunc = NULL_ENTRY;
        insertStubTable[i].oriCode = 0;
	}

    insertStubTable[0].asm_tramp_addr = (uint32_t )asm_trampoline_slotA;
    insertStubTable[0].insertFuncAddr = (uint32_t )InsertFunC_A;
    insertStubTable[1].asm_tramp_addr = (uint32_t )asm_trampoline_slotB;
    insertStubTable[1].insertFuncAddr = (uint32_t )InsertFunC_B;
    insertStubTable[2].asm_tramp_addr = (uint32_t )asm_trampoline_slotC;
    insertStubTable[2].insertFuncAddr = (uint32_t )InsertFunC_C;
    insertStubTable[3].asm_tramp_addr = (uint32_t )asm_trampoline_slotD;
    insertStubTable[3].insertFuncAddr = (uint32_t )InsertFunC_D;
    insertStubTable[4].asm_tramp_addr = (uint32_t )asm_trampoline_slotE;
    insertStubTable[4].insertFuncAddr = (uint32_t )InsertFunC_E;
    insertStubTable[5].asm_tramp_addr = (uint32_t )asm_trampoline_slotF;
    insertStubTable[5].insertFuncAddr = (uint32_t )InsertFunC_F;
    insertStubTable[6].asm_tramp_addr = (uint32_t )asm_trampoline_slotG;
    insertStubTable[6].insertFuncAddr = (uint32_t )InsertFunC_G;
    insertStubTable[7].asm_tramp_addr = (uint32_t )asm_trampoline_slotH;
    insertStubTable[7].insertFuncAddr = (uint32_t )InsertFunC_H;
    insertStubTable[8].asm_tramp_addr = (uint32_t )asm_trampoline_slotI;
    insertStubTable[8].insertFuncAddr = (uint32_t )InsertFunC_I;
    insertStubTable[9].asm_tramp_addr = (uint32_t )asm_trampoline_slotJ;
    insertStubTable[9].insertFuncAddr = (uint32_t )InsertFunC_J;
    stubCount = 0;
    insertStubCount = 0;
}

/*******************************************************************************
*
*  verInstallStub - install stub routine
*
*  This routine stubs a routine pointed to by <stubbed> with a function
*  specified by <stub>. Both routines MUST have the same declaration.
*
*  Maximum number of stubs allowed by the mechanism is defined in Core-OS.
*
*  Stubs should be uninstalled by means of the verUninstallAllStubs() routine
*  as soon as possible or verUninstallStub().
*
*  RETURNS: VER_OK on success, otherwise VER_ERROR.
*
* ERRNO: N/A
*/
uint32_t verInstallStub(void * oriAddr, void *  jumpAddr, uint32_t StubType) 
{
    uint32_t retVal = 10;
	retVal = installStub((uint32_t)oriAddr, (uint32_t)jumpAddr, StubType);
    return retVal;
}


/*******************************************************************************
*
*  verUninstallStub - uninstall stub routine
*
*  This routine uninstalls specified stub previusly installed by
*  verInstallStub().
*
*  RETURNS: VER_OK on success, otherwise VER_ERROR.
*
*  ERRNO: N/A
*/
uint32_t verUninstallStub(void * oriAddr, uint32_t StubType) {
	uint32_t retVal = 2;
	retVal = uninstallStub((uint32_t)oriAddr, StubType);
	return retVal;
}


/*******************************************************************************
*
*  verUninstallAllStubs - uninstall all stub routines
*
*  This routine uninstalls all stubs previusly installed by verInstallStub().
*
*  RETURNS: VER_OK on success, otherwise VER_ERROR.
*
*  ERRNO: N/A
*/
VER_STATUS verUninstallAllStubs(uint32_t StubType)
{
	for (int i = 0; i < MAX_STUBS; i++) 
    {
        if(StubType != 1)
        {
            if(stubTable[i].original != NULL_ENTRY)
            {
                verRecoverFunc((uint32_t)stubTable[i].original, stubTable[i].oriCode);
                stubTable[i].original = NULL_ENTRY;
		        stubTable[i].stub = NULL_ENTRY;
                stubTable[i].oriCode = 0;
            }
        }

        if(StubType != 0)
        {
            if(insertStubTable[i].target != NULL_ENTRY)
            {
                verRecoverFunc((uint32_t)insertStubTable[i].target, insertStubTable[i].oriCode);
                insertStubTable[i].target = NULL_ENTRY;
		        insertStubTable[i].custHookFunc = NULL_ENTRY;
                insertStubTable[i].oriCode = 0;
            }
        }
	}

    if(StubType != 1)
    {
        stubCount = 0;
    }
    
    if(StubType != 0)
    {
        insertStubCount = 0;
    }
}

// instal stub
// addr---original function addr, jump---stub addr, stubType---0 for replace, 1 for insert function(to be develop)
uint32_t installStub(uint32_t addr, uint32_t jump, uint32_t StubType) {
	int i;
	if (StubType == 0) {

        if (stubCount >= MAX_STUBS) {
			return 1; // stub is full, return 1
		}

		if (addr == NULL_ENTRY || jump == NULL_ENTRY) {
			return 2; // original or jump fuction addr is empty, return 2
		}
		
		for (i = 0; i < MAX_STUBS; i++) {
			if ((uint32_t)stubTable[i].original == addr) {
				if (stubTable[i].stub != NULL_ENTRY) {
					return 3; // already has stub for original function	, return 1
				}
				stubTable[i].stub = (void * )jump;
                stubTable[i].oriCode = *(volatile uint32_t *)addr;
                verFuncRedirect(addr, jump);
				return 0;
			}
		}

        for (i = 0; i < MAX_STUBS; i++) {
			if ((uint32_t)stubTable[i].original == NULL_ENTRY) {
		        stubTable[i].original = (void * )addr;
		        stubTable[i].stub = (void * )jump;
                stubTable[i].oriCode = *(volatile uint32_t *)addr;
                verFuncRedirect(addr, jump);
                stubCount++;
				return 0;
			}
		}

		return 4; // the stub table and count has error

	}

	if (StubType == 1) {

        if (insertStubCount >= MAX_STUBS) {
			return 1; // stub is full, return 1
		}

		if (addr == NULL_ENTRY || jump == NULL_ENTRY) {
			return 2; // original or jump fuction addr is empty, return 2
		}
		
		for (i = 0; i < MAX_STUBS; i++) {
			if ((uint32_t)insertStubTable[i].target == addr) {
				if (insertStubTable[i].custHookFunc != NULL_ENTRY) {
					return 3; // already has insert stub for original function	, return 3
				}
				insertStubTable[i].custHookFunc = (void * )jump;
                insertStubTable[i].oriCode = *(volatile uint32_t *)addr;
                ppc_code_write(insertStubTable[i].asm_tramp_addr, *(volatile uint32_t *)addr);
                verFuncRedirect(insertStubTable[i].asm_tramp_addr + 4, addr + 4);
                verFuncRedirect(addr, insertStubTable[i].insertFuncAddr);
				return 0;
			}
		}

        for (i = 0; i < MAX_STUBS; i++) {
			if ((uint32_t)insertStubTable[i].target == NULL_ENTRY) {
		        insertStubTable[i].target = (void * )addr;
		        insertStubTable[i].custHookFunc = (void * )jump;
                insertStubTable[i].oriCode = *(volatile uint32_t *)addr;
                ppc_code_write(insertStubTable[i].asm_tramp_addr, *(volatile uint32_t *)addr);
                verFuncRedirect(insertStubTable[i].asm_tramp_addr + 4, addr + 4);
                verFuncRedirect(addr, insertStubTable[i].insertFuncAddr);
                insertStubCount++;
				return 0;
			}
		}

		return 4; // the stub table and count has error

	}

    return 5;//the stub type unkown
}

// uninstall stub
// addr---original function addr
uint32_t uninstallStub(uint32_t addr, uint32_t StubType) {
	int i;
    if(StubType == 0)
    {
	    for (i = 0; i < MAX_STUBS; i++) {
		    if ((uint32_t)stubTable[i].original == addr) {
                verRecoverFunc(addr, stubTable[i].oriCode);
                stubTable[i].original = NULL_ENTRY;
			    stubTable[i].stub = NULL_ENTRY;
                stubTable[i].oriCode = 0;
                stubCount--;
			    return 0; // uninstall successfully, return 0
		    }
	    }
	    return 1; // can't find addr in stub table, return 1
    }

    if(StubType == 1)
    {
	    for (i = 0; i < MAX_STUBS; i++) {
		    if ((uint32_t)insertStubTable[i].target == addr) {
                verRecoverFunc(addr, insertStubTable[i].oriCode);
                insertStubTable[i].target = NULL_ENTRY;
			    insertStubTable[i].custHookFunc = NULL_ENTRY;
                insertStubTable[i].oriCode = 0;
                insertStubCount--;
			    return 0; // uninstall successfully, return 0
		    }
	    }
	    return 1; // can't find addr in stub table, return 1
    }


    return 2; //stub type invalid
}


/*************************************************************************
*
* verInstallSpy - install spy hook which monitor access to first 8 bytes
*                 from specified memory address
*
* Parameters:
*   mode - type of access to monitor:
*             SPY_RD - read
*             SPY_WR - write
*             SPY_RDWR - read/write
*   addr - address of memory (note: address is aligned to 8-byte boundary)
*   fn   - spy hook which is called after access to monitored memory.
*     Example: void spyHook(int mode, void *addr){}
*       where <addr> is address of read memory in case of <mode>==SPY_RD or
*             <addr> is address of wrriten memory in case of <mode>==SPY_WR
*
* RETURNS: VER_OK on success, otherwise VER_ERROR
*
* ERRNO: N/A
*/
VER_STATUS verInstallSpy(int mode, void *addr, SPY_RTN fn)
{
    VER_STATUS retVal;
    if (mode==SPY_RD || mode==SPY_WR || mode==SPY_RDWR)
    {
        if ((verSpyHookAddr == NULL) && (fn!= NULL))
        {
            verSpyHookAddr = fn;
            _verSpyEnable(mode, addr);
            retVal = VER_OK;
        } 
        else
        {
            retVal = VER_ERROR;
        }
    }
    else
    {
        retVal = VER_ERROR;
    }
    return retVal;
}

/*************************************************************************
*
* verSetSpyAddr - sets memory address for spy
*
* This routine sets memory address for spy. It can be used inside spy
* hook to change monitored memory address without instaling/uninstaling
* spy.
*
* RETURNS: VER_OK on success, otherwise VER_ERROR.
*
* ERRNO: N/A
*/
VER_STATUS verSetSpyAddr (int mode, void *addr)
{
    VER_STATUS retVal;
    if (mode==SPY_RD || mode==SPY_WR || mode==SPY_RDWR)
    {
        if (verFlashStub) 
        {
            return VER_ERROR;
   	    }

        if (verSpyHookAddr != NULL)
        {
            _verSpyEnable(mode, addr);
            retVal = VER_OK;;
        } 
        else
        {
            retVal = VER_ERROR;
        }
    }
    else
    {
        retVal = VER_ERROR;
    }

    return retVal;
}


/*******************************************************************************
*
*  verUninstallSpy - uninstall spy hook
*
*  This routine uninstall spy previusly installed by verInstallSpy().
*
*  RETURNS: VER_OK on success, otherwise VER_ERROR.
*
*  ERRNO: N/A
*/

VER_STATUS verUninstallSpy(void) 
{
    VER_STATUS retVal;
    if (verSpyHookAddr != NULL)
    {
        _verSpyDisable();
        verSpyHookAddr = NULL;
        retVal = VER_OK;
    }
	else
	{
	    retVal = VER_ERROR;
    }
    return retVal;
}

void IVOR15Handler_Spy(void)
{
    int i = 0;
    void *ptr = NULL_ENTRY;
    verSpyHookAddr(i, ptr);
}

CPU_CRT_STATE checkCrtState (void)
{
    CPU_SR	sr;
    sr =  CPU_SR_Rd();  // 读sr
    if((sr & 0x00008000) == 0)
    {
        return CPU_CRT_ENTER;
    }
    else
    {
        return CPU_CRT_EXIT;
    }
}

void verCheckSysStatus (void)
{
    sysStatus = 0;
    CPU_INT32U    i;
    OS_RDY_LIST  *p_rdy_list;
    for (i = 0u; i < OS_CFG_PRIO_MAX; i++) {
        p_rdy_list = &OSRdyList[i];
        if(p_rdy_list->HeadPtr != (OS_TCB *)0 || p_rdy_list->TailPtr != (OS_TCB *)0)
        {
            if( (i != 10) && (i != OS_CFG_PRIO_MAX - 1) && (i != OS_CFG_PRIO_MAX - 3))
            {
                 sysStatus += 0x01;
                 break;
            }
        }
    }

    if((OSPrioTbl[0] & 0xFFDFFFFF) != 0 )
    {
        sysStatus += 0x10;
    }

    if((OSPrioTbl[1] & 0xFFFFFFFA) != 0 )
    {
        sysStatus += 0x20;
    }

    if(OSPrioCur != 10)
    {
        sysStatus += 0x100;
    }

    if(OSTCBCurPtr->TickNextPtr != (OS_TCB *)0 )
    {
        sysStatus += 0x1000;
    }
    if( OSTCBCurPtr->TickPrevPtr != (OS_TCB *)0)
    {
        sysStatus += 0x2000;
    }
    if( OSTCBCurPtr->NextPtr != (OS_TCB *)0)
    {
        sysStatus += 0x4000;
    }
    if( OSTCBCurPtr->PrevPtr != (OS_TCB *)0)
    {
        sysStatus += 0x8000;
    }

    if(OSTickList.TCB_Ptr != (OS_TCB *)0)
    {
        sysStatus += 0x10000;
    }

    if(OSMsgPool.NbrFree != OSCfg_MsgPoolSize)
    {
        sysStatus += 0x100000;
    }
    if(OSMsgPool.NbrUsed != 0)
    {
        sysStatus += 0x200000;
    }

    if(OSTmrTaskTCB.TaskState != OS_TASK_STATE_RDY && OSTmrTaskTCB.TaskState != OS_TASK_STATE_PEND)
    {
        sysStatus += 0x1000000;
    }
    if(OSTmrMutex.OwnerTCBPtr != &OSTmrTaskTCB && OSTmrMutex.OwnerTCBPtr != (OS_TCB *)0)
    {
        sysStatus += 0x2000000;
    }
}

void writeSysStatusComment(void)
{
    char statusComment[VER_MAX_COMMENT_LENGTH];
    verMemset(statusComment, '\0', VER_MAX_COMMENT_LENGTH);
    verStrcpy(statusComment, "PRE-CHECK ERROR: ");
    verStrcat(statusComment, verXtoa(sysStatus));
    verComment(statusComment);
}
