/*****************************************************************************
 *   File:     THCL.c 
 *   Author :  vmg/vjw 
 *   Purpose:  This library shall provide implementation of API for the test
 *             harness protocol layer. 
 *   Remarks:  
 *****************************************************************************/


/* includes */
   #include "THCL.h"
   #include "stdio.h"
   /*test the uart*/
#define CONFIG_SYS_CCSRBAR 0xe0000000
#define CONFIG_SYS_CCSRBAR_PHYS 0xFE0000000ULL
#define CFG_SYS_NS16550_COM1	(CONFIG_SYS_CCSRBAR+0x4500)
#define CFG_SYS_NS16550_COM1_UDSR	(CONFIG_SYS_CCSRBAR+0x4510)



   volatile unsigned char * const UART0DR = (unsigned char *)CFG_SYS_NS16550_COM1;
    volatile unsigned char * const UART0UDSR = (unsigned char *)CFG_SYS_NS16550_COM1_UDSR;
	
   void putc_uart0(unsigned char *s)
   {
    int i,j=0;

		for(i=0;i++;i<10000)
        {
            for(j=0;j++;j<10000)
            {
                ;
            }
        }
	   if(*s != '\0')
	   { /* Loop until end of string */
		   *UART0DR = (unsigned char)(*s); /* Transmit char */
	//	   s++; /* Next char */
	   }
	    for(i=0;i++;i<180000)
        {
            for(j=0;j++;j<180000)
            {
                ;
            }
        }
   }  
   
   int getc_uart0(unsigned char *pbuf)
   {
	   int i,j=0;
  #if 1
	   int count = 0; // 计数器，记录循环次数
	   int max_attempts = 1000000; // 最大尝试次数

	   
	   while (count < max_attempts)
	   {
	   	*pbuf = (unsigned char)(*UART0DR);	
		  if (*pbuf !=0) 
		   { 
	   
			   for(i=0;i++;i<180000)
			  {
				  for(j=0;j++;j<180000)
				  {
					  ;
				  }
			  }
			   return 0;
	   
		   }
		  else
		   {		   
			   for(i=0;i++;i<180000)
			   {
				   for(j=0;j++;j<180000)
				   {
					   ;
				   }
			   }
			  count++;
			  continue; // 继续循环进行下一次判断
		   }
	   }
	   return 1;

#endif






#if 0

	   for(i=0;i++;i<10000)
	   {
		   for(j=0;j++;j<10000)
		   {
			   ;
		   }
	   }

	   //if(*pbuf != '\0')
	   { /* Loop until end of string */
		   *pbuf = (unsigned char)(*UART0DR); /* Transmit char */
		//	pbuf++; /* Next char */
		//	if(*pbuf == '\0')
		//	   break;
	   }
	   for(i=0;i++;i<180000)
	   {
		   for(j=0;j++;j<100000)
		   {
			   ;
		   }
	   }
 #endif

   }  


/* imports */
 //  extern UINT64  sysTimestamp64Get (void);


//   static SIO_CHAN *			pSioChan;	/* serial I/O channel */

   int THCLReadByte (unsigned char *addr, unsigned char *c)
   {
	   ;
   }
   int THCLWriteByte (unsigned char *addr, unsigned char *c)
   {
	   ;
   }
/*****************************************************************************
 *   Function: GetTime
 *   Returns:  time [msec]
 *   Globals:  
 *   Purpose:  This function shall get current time.
 *   Comments: 
 *****************************************************************************/
   static int GetTime()
   {
   	 // return sysTimestamp64DiffToUsec(sysTimestamp64Get(), 0) / 1000;
	   ;
   }

/*****************************************************************************
 *   Function: Open
 *   Returns:   0 - success
 *             -1 - error
 *   Globals:  
 *   Purpose:  This function shall open the serial device.
 *   Comments:    
 *****************************************************************************/

   int THCLOpen(void)
   {
//init uart,set the baud_rate and choose the port 
   //need to add new function

//		lq_serial_init(120000000,0, 115200);
      return 0;
   }      

/*****************************************************************************
 *   Function: Close
 *   Returns:  
 *   Globals:  
 *   Purpose:  This function shall close the serial device.
 *   Comments:    
 *****************************************************************************/

   void THCLClose(void)
   {
   /* do nothing */   
   }      

/*****************************************************************************
 *   Function: GetChar
 *   Returns:   0 - success
 *             -1 - error
 *             -2 - timeout    
 *   Globals:  
 *   Purpose:  This function shall read character from the serial device
 *             in the specified time [msec].
 *   Comments: If <timeout> = -1 then wait forever.        
 *****************************************************************************/

   int THCLGetChar(char *c, long timeout)
   {
   #if 0
   	   unsigned char buf='F';
	   if (0 !=getc_uart0(c))
	   	{
	   		putc_uart0(&buf);
			return -1;
		};
#endif
	  getc_uart0(c);

      return 0; 
   }      

/*****************************************************************************
 *   Function: PutChar
 *   Returns:   0 - success
 *             -1 - error
 *             -2 - timeout    
 *   Globals:  
 *   Purpose:  This function shall write character to the serial device
 *             in the specified time [msec].
 *   Comments: If <timeout> = -1 then wait forever.        
 *****************************************************************************/

   int THCLPutChar(char c, long timeout)
   {
   	putc_uart0(&c);
      return 0; 
   }      
