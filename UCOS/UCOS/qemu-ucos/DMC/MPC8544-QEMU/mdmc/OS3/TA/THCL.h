/*****************************************************************************
 *   File:     THCL.h 
 *   Author :  vmg 
 *   Purpose:  This file shall provide API for the test harness communication
 *             layer. 
 *   Remarks:  
 *****************************************************************************/

#ifndef THCL
#define THCL

#define THCL_OK                0
#define THCL_ERROR            -1
#define THCL_IO_ERROR         -2
#define THCL_IO_TIMEOUT       -3

#define TH_TTY_CHANNEL 1
#define TH_TTY_BAUD 57600

/*****************************************************************************
 *   Function: THCLOpen
 *   Returns:  THCL_OK
 *             THCL_ERROR
 *   Purpose:  This function shall open the serial device.
 *   Comments:    
 *****************************************************************************/

   extern int THCLOpen(void);

/*****************************************************************************
 *   Function: THCLClose
 *   Returns:  N/A
 *   Purpose:  This function shall close the serial device.
 *   Comments:    
 *****************************************************************************/

   extern void THCLClose(void);

/*****************************************************************************
 *   Function: THCLGetChar
 *   Returns:  THCL_OK
 *             THCL_IO_ERROR
 *             THCL_IO_TIMEOUT
 *   Purpose:  This function shall read character from the serial device
 *             in the specified time [msec].
 *   Comments: If <timeout> = -1 then wait forever.        
 *****************************************************************************/

   extern int THCLGetChar(char *c, long timeout);

/*****************************************************************************
 *   Function: THCLPutChar
 *   Returns:  THCL_OK
 *             THCL_IO_ERROR
 *             THCL_IO_TIMEOUT
 *   Purpose:  This function shall write character to the serial device
 *             in the specified time [msec].
 *   Comments: If <timeout> = -1 then wait forever.     
 *****************************************************************************/

   extern int THCLPutChar(char c, long timeout);

/*****************************************************************************
 *   Function: THCLPutCharDebug
 *   Returns:  THCL_OK
 *             THCL_IO_ERROR
 *             THCL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall write character to the serial debug device
 *             in the specified time [msec].
 *   Comments: If <timeout> = -1 then wait forever.        
 *****************************************************************************/

   extern int THCLPutCharDebug(char c, long timeout);

/*****************************************************************************
 *   Function: THCLReadByte
 *   Returns:  THCL_OK
 *             THCL_IO_ERROR
 *             THCL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall read one byte from memory.
 *   Comments: 
 *****************************************************************************/

   extern int THCLReadByte (unsigned char *addr, unsigned char *c);

/*****************************************************************************
 *   Function: THCLWriteByte
 *   Returns:  THCL_OK
 *             THCL_IO_ERROR
 *             THCL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall write one byte to memory.
 *   Comments: 
 *****************************************************************************/

   extern int THCLWriteByte (unsigned char *addr, unsigned char *c);

/*****************************************************************************
 *   Function: THCLPutCharDebug
 *   Returns:  THCL_OK
 *             THCL_IO_ERROR
 *             THCL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall write character to the serial debug device
 *             in the specified time [msec].
 *   Comments: If <timeout> = -1 then wait forever.        
 *****************************************************************************/

   extern int THCLPutCharDebug(char c, long timeout);


#endif  /* THCL */
