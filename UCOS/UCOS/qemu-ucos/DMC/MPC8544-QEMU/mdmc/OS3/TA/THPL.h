/*****************************************************************************
 *   File:     THPL.h 
 *   Author :  vmg 
 *   Purpose:  This file provides API for the test harness protocol layer. 
 *   Remarks:  
 *****************************************************************************/

#ifndef THPL
#define THPL

/* defines */
   #define THPL_OK                          THCL_OK
   #define THPL_ERROR                       THCL_ERROR
   #define THPL_IO_ERROR                    THCL_IO_ERROR
   #define THPL_IO_TIMEOUT                  THCL_IO_TIMEOUT
   #define THPL_END_OF_DATA                 -4
   #define THPL_INVALID_CRC                 -5
   #define THPL_INVALID_DATA                -6
   #define THPL_INVALID_PARAM               -7

   #ifndef IO_TIMEOUT   
   #define IO_TIMEOUT   5000
   #endif /* IO_TIMEOUT */
typedef enum   TH_CMD_VALUE_TYPE
{
    RUN_TEST_CMD = 1,  /* run test;
                           Data: mode (int), number of parts on target (int) */
    REPORT_CMD = 2,  /* send results of test to host;
                           Data: none */
    CACHE_UPDATE_CMD = 3,  /* Cache data text update;
                           Data: address, size */
    SET_PARAMS_CMD = 4,  /* set test parameters;
                           Data: param1, param2 */
    RESET_CMD = 5,  /* reset target;
                           Data: none */
    SET_TIMEOUT_CMD = 6,  /* set test timeout;
                           Data: timeout in sec */
    BEFORE_TEST_LOAD_CMD = 7,  /* hook called before test SREC load;
                           Data: none */
    SET_RUN_ADDR_CMD = 8,  /* set run address;
                           Data: run addr */
    CTX_SWITCH_CMD = 9   /* switch memory context to the specified partition num.;
                           Data: partition number */

} TH_CMD_TYPE;

/* types */
   typedef void (*cmdFn_t)(void *param1, void *param2);

/*****************************************************************************
 *   Function: THPLInit
 *   Returns:  THPL_OK
 *             THPL_ERROR
 *   Globals:  cmdTlb
 *   Purpose:  This function initialize the THPL library.
 *   Comments:    
 *****************************************************************************/

   extern int THPLInit(int commTimeout);

/*****************************************************************************
 *   Function: THPLStart
 *   Returns:  N/A
 *   Globals:  
 *   Purpose:  This function shall start the THPL library.
 *   Comments: This function never returns to the caller.    
 *****************************************************************************/

   extern void THPLStart(void);

/*****************************************************************************
 *   Function: THPLStartTextMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall start sending of a text message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLStartTextMsg(void);

/*****************************************************************************
 *   Function: THPLFinishTextMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall finish sending of a text message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLFinishTextMsg(void);

/*****************************************************************************
 *   Function: THPLPutCharToMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *             THPL_INVALID_PARAM
 *   Globals:  crcMsg
 *   Purpose:  This function shall put given character to a text message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLPutCharToMsg(unsigned char c);

/*****************************************************************************
 *   Function: THPLStartDataMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall start sending of a data message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLStartDataMsg(unsigned char *addr);

/*****************************************************************************
 *   Function: THPLFinishDataMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall finish sending of a data message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLFinishDataMsg(void);

/*****************************************************************************
 *   Function: THPLPutByteToMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall put given byte to a data message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLPutByteToMsg(unsigned char c);

/*****************************************************************************
 *   Function: THPLInstallCmd
 *   Returns:  THPL_OK
 *             THPL_INVALID_PARAM
 *   Globals:  cmdTlb
 *   Purpose:  This function shall install new command.
 *   Comments:    
 *****************************************************************************/

   extern int THPLInstallCmd(unsigned char cmd, cmdFn_t fn);

/*****************************************************************************
 *   Function: THPLSendAckMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall send acknowledge message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLSendAckMsg(int val);

/*****************************************************************************
 *   Function: THPLSendNackMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT 
  *   Globals:  
 *   Purpose:  This function shall send acknowledge message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLSendNackMsg(int val);

/*****************************************************************************
 *   Function: THPLSendHelloMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall send hello message.
 *   Comments:    
 *****************************************************************************/

   extern int THPLSendHelloMsg(void);

#endif  /* THPL */
