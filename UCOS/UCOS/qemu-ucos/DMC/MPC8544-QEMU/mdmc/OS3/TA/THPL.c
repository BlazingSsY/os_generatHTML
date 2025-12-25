/*****************************************************************************
 *   File:     THPL.c
 *   Author :  vmg
 *   Purpose:  This library shall provide implementation of API for the test
 *             harness protocol layer.
 *   Remarks:
 *****************************************************************************/

#ifdef __cplusplus
extern "C" {
#endif

/* includes */
   #include "THPL.h"
   #include "THCL.h"
   #include  <os.h>

/* defines */
//   #define IO_TIMEOUT   1000

/* prototypes */
   static int ioTimeout = 1000;
   static void InstallCmd(void *param1, void *param2);
   static void ProcessExecMsg(void);
   static void ProcessLoadMsg(void);
   static void ProcessReadMsg(void);
   static void ProcessPingMsg(void);
   static int ReceiveExecMsg(unsigned char *cmd, void **param1, void **param2);
   static int ReceiveLoadMsg(void);
   static int ReceiveReadMsg(unsigned char **addr, unsigned long *len);
   static int ReceivePingMsg(void);
   static int SendDataMsg(unsigned char *addr, unsigned long len);
   static int PutChar(unsigned char c);
   static int PutByte(unsigned char c);
   static int PutWord(unsigned long c);
   static int GetChar(unsigned char *c);
   static int GetByte(unsigned char *c);
   static int GetWord(unsigned long *c);
   static int Bcd2Dec(unsigned char bcd, unsigned char *c);
   static unsigned char Dec2BcdLo(unsigned char c);
   static unsigned char Dec2BcdHi(unsigned char c);

/* globals */
   static cmdFn_t cmdTlb[10];  /* command table */
   static unsigned long crcMsg;  /* LS of current message */  
   static unsigned long lsMsg; 
   static char lastChar = 0;    /* last character read from the port */ 
/* externs */
   extern unsigned long CRC32Accumulate(unsigned long crc, unsigned char byte);
   
/*****************************************************************************
 *   Function: THPLInit
 *   Returns:  THPL_OK
 *             THPL_ERROR
 *   Globals:  cmdTlb
 *   Purpose:  This function initialize the THPL library.
 *   Comments:    
 *****************************************************************************/

   int THPLInit(int commTimeout)
   {
      int i;
	  unsigned char ic = 'Y';

      ioTimeout = commTimeout;
   /* initialize the THCL */
	  //need to add new function
      THCLPutChar(ic,1100);

      if (THCLOpen() != THCL_OK)
         return THPL_ERROR;           

   /* reset command table */
      for (i=0; i<10; i++)
         cmdTlb[i] = 0;            

   /* register default command */
      cmdTlb[0] = InstallCmd;   

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLStart
 *   Returns:  N/A
 *   Globals:  
 *   Purpose:  This function shall start the THPL library.
 *   Comments: This function never returns to the caller.    
 *****************************************************************************/

   void THPLStart(void)
   {
      OS_ERR  os_err;
      unsigned char c;
      while (1)
      {
         //OSTimeDly(1, OS_OPT_TIME_DLY, &os_err);

         if (lastChar != 0x01)
         {
         /* wait for a message forever */
		 	  //need to add new function
            if (GetChar(&c) != THPL_OK)
               continue;

         /* check that it is the head of a message */
            if (c != 0x01)
            {
         //   	ic = 'N';
		 //		THCLPutChar(ic,1100);
               continue;
			}
         }

      /* wait for type of a message */
		 	  //need to add new function
         if (GetChar(&c) != THPL_OK)
           continue;
         
      /* decode type of a message */
         switch (c)
         {
         /* is it Exec message? */
            case 0x10: ProcessExecMsg(); break;

         /* is it Load message? */
            case 0x11: ProcessLoadMsg(); break;

         /* is it Read message? */
            case 0x12: ProcessReadMsg(); break;

         /* is it Ping message? */
			
            case 0x13: ProcessPingMsg(); break;
			
         }
	 //OSTimeDly(100, OS_OPT_TIME_DLY, &os_err);
      }

   }

/*****************************************************************************
 *   Function: THPLStartTextMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall start sending of a text message.
 *   Comments:    
 *****************************************************************************/

   int THPLStartTextMsg(void)
   {
      int res;

   /* initialize LS for the message */
      crcMsg = 0xFFFFFFFF;  
      
   /* send head of the message */
      if ((res = PutChar(0x01)) != THPL_OK)
         return res;

   /* send the message type */
      if ((res = PutChar(0x19)) != THPL_OK)
         return res;

   /* calculate CRC */
      crcMsg = CRC32Accumulate(crcMsg, 0x19);

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLFinishTextMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall finish sending of a text message.
 *   Comments:    
 *****************************************************************************/

   int THPLFinishTextMsg(void)
   {
      int res;
      
   /* send CRC of the message */
      if ((res = PutWord(crcMsg)) != THPL_OK)
         return res;

   /* send tail of the message */
      if ((res = PutChar(0x02)) != THPL_OK)
         return res;

      return THPL_OK;
   }

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

   int THPLPutCharToMsg(unsigned char c)
   {
      int res;
      
   /* check code of given character */
      if (c < 32 && c != 10 && c != 13)
         return THPL_INVALID_PARAM;

   /* send given character */
      if ((res = PutChar(c)) != THPL_OK)
         return res;

   /* calculate CRC for the message */
      crcMsg = CRC32Accumulate(crcMsg, c);
   
      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLStartDataMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall start sending of a data message.
 *   Comments:    
 *****************************************************************************/

   int THPLStartDataMsg(unsigned char *addr)
   {
      int res;
      int i;
      
   /* initialize CRC for the message */
      crcMsg = 0xFFFFFFFF;  
      
   /* send head of the message */
      if ((res = PutChar(0x01)) != THPL_OK)
         return res;

   /* send the message type */
      if ((res = PutChar(0x18)) != THPL_OK)
         return res;

   /* calculate CRC */
      crcMsg = CRC32Accumulate(crcMsg, 0x18);

   /* send given address */
      if ((res = PutWord(*(unsigned long*) &addr)) != THPL_OK)
         return res;

   /* calculate CRC */
      for (i = 0; i < 4; i++)
         crcMsg = CRC32Accumulate(
            crcMsg,
            (unsigned char) ((*(unsigned long*) &addr >> (i * 8)) & 0xFF)
         );  

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLFinishDataMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall finish sending of a data message.
 *   Comments:    
 *****************************************************************************/

   int THPLFinishDataMsg(void)
   {
      int res;
      
   /* send CRC of the message */
      if ((res = PutWord(crcMsg)) != THPL_OK)
         return res;

   /* send tail of the message */
      if ((res = PutChar(0x02)) != THPL_OK)
         return res;

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLPutByteToMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  crcMsg
 *   Purpose:  This function shall put given byte to a data message.
 *   Comments:    
 *****************************************************************************/

   int THPLPutByteToMsg(unsigned char c)
   {
      int res;
      
   /* send given character */
      if ((res = PutByte(c)) != THPL_OK)
         return res;

   /* calculate CRC for the message */
      crcMsg = CRC32Accumulate(crcMsg, c);
   
      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLInstallCmd
 *   Returns:  THPL_OK
 *             THPL_INVALID_PARAM
 *   Globals:  cmdTlb
 *   Purpose:  This function shall install new command.
 *   Comments:    
 *****************************************************************************/

   int THPLInstallCmd(unsigned char cmd, cmdFn_t fn)
   {
   /* check that caller tries to install user's command */
      if (cmd == 0)
         return THPL_INVALID_PARAM; 

   /* register the specified command function in the command table */
      cmdTlb[cmd] = fn;   

      return THPL_OK;
   }


/*****************************************************************************
 *   Function: InstallCmd
 *   Returns:  N/A
 *   Globals:  
 *   Purpose:  This function initialize the THPL library.
 *   Comments:    
 *****************************************************************************/

   static void InstallCmd(void *param1, void *param2)
   {
      int res;
      
   /* install command */   
      if ((res = THPLInstallCmd(*(unsigned char*) &param1, (cmdFn_t) param2)) != THPL_OK)
      {
      /* send Non-Acknowladge message */
         THPLSendNackMsg(res);
         
         return;
      }
      
   /* send acknowledge message */
      THPLSendAckMsg(THPL_OK);      
   }

/*****************************************************************************
 *   Function: ProcessExecMsg
 *   Returns:  N/A
 *   Globals:  cmdTlb
 *   Purpose:  This function shall process the exec message.
 *   Comments:    
 *****************************************************************************/

   static void ProcessExecMsg(void)
   {
      unsigned char cmd;
      void *param1;
      void *param2;
      int res;

   /* receive message */   
      if ((res = ReceiveExecMsg(&cmd, &param1, &param2)) != THPL_OK)
      {
      /* send Non-Acknowladge message */
         THPLSendNackMsg(res);

         return;
      }

   /* send acknowledge message */
      if (THPLSendAckMsg(THPL_OK) != THPL_OK)
         return;      

   /* execute command if it is installed */
      if (cmdTlb[cmd])
         cmdTlb[cmd](param1, param2);
   }

/*****************************************************************************
 *   Function: ProcessLoadMsg
 *   Returns:  N/A
 *   Globals:  
 *   Purpose:  This function shall process the load message.
 *   Comments:    
 *****************************************************************************/

   static void ProcessLoadMsg(void)
   {
      int res;
      
   /* receive message */   
      if ((res = ReceiveLoadMsg()) != THPL_OK)
      {
      /* send Non-Acknowladge message */
         THPLSendNackMsg(res);

         return;
      }
      
   /* send acknowledge message */
      THPLSendAckMsg(THPL_OK);      
   }

/*****************************************************************************
 *   Function: ProcessReadMsg
 *   Returns:  N/A
 *   Globals:  
 *   Purpose:  This function shall process the read message.
 *   Comments:    
 *****************************************************************************/

   static void ProcessReadMsg(void)
   {
      unsigned char *addr;
      unsigned long len;      
      int res;
      
   /* receive message */   
      if ((res = ReceiveReadMsg(&addr, &len)) != THPL_OK)
      {
      /* send Non-Acknowladge message */
         THPLSendNackMsg(res);
      
         return;
      }
      
   /* send data from the specified location */   
      if ((res = SendDataMsg(addr, len)) != THPL_OK)
      {
      /* send Non-Acknowladge message */
         THPLSendNackMsg(res);
      }
   }

/*****************************************************************************
 *   Function: ProcessPingMsg
 *   Returns:  N/A
 *   Globals:  
 *   Purpose:  This function shall process the ping message.
 *   Comments:    
 *****************************************************************************/

   static void ProcessPingMsg(void)
   {
      int res;
      
   /* receive message */   
      if ((res = ReceivePingMsg()) != THPL_OK)
      {
      /* send Non-Acknowladge message */
         THPLSendNackMsg(res);

         return;
      }
      
   /* send acknowledge message */
      THPLSendAckMsg(THPL_OK);      
   }

/*****************************************************************************
 *   Function: ReceiveReadMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *             THPL_END_OF_DATA  
 *             THPL_INVALID_DATA 
 *             THPL_INVALID_CRC
 *   Globals:  
 *   Purpose:  This function shall receive the read message.
 *   Comments:    
 *****************************************************************************/

   static int ReceiveReadMsg(
      unsigned char **addr,
      unsigned long *len
   )
   {
      unsigned long crcRcvd, sum = 0xFFFFFFFF;
      unsigned char c;
      int res, i;
      
   /* calculate CRC */
      sum = CRC32Accumulate(sum, 0x12);  
      
   /* get address of data */
      if ((res = GetWord((unsigned long*) addr)) != THPL_OK)
         return res;

   /* calculate CRC */
      for (i = 0; i < 4; i++)
         sum = CRC32Accumulate(
            sum,
            (unsigned char) (((unsigned long) *addr >> (i * 8)) & 0xFF)
         );  

   /* get length of data */
      if ((res = GetWord(len)) != THPL_OK)
         return res;

   /* calculate CRC */
      for (i = 0; i < 4; i++)
         sum = CRC32Accumulate(
            sum,
            (unsigned char) ((*len >> (i * 8)) & 0xFF)
         );  

   /* get CRC from the packet */
      if ((res = GetWord(&crcRcvd)) != THPL_OK)
         return res;

   /* get tail of the message */
      if ((res = GetChar(&c)) != THPL_OK)
         return res;
         
      if (c != 0x02)
         return THPL_INVALID_DATA;

      if (sum != crcRcvd)
         return THPL_INVALID_CRC;

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: ReceiveExecMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *             THPL_END_OF_DATA 
 *             THPL_INVALID_DATA 
 *             THPL_INVALID_CRC
 *   Globals:  
 *   Purpose:  This function shall receive the exec message.
 *   Comments:    
 *****************************************************************************/

   static int ReceiveExecMsg(
      unsigned char *cmd,
      void **param1,
      void **param2)
   {
      unsigned long crcRcvd, sum = 0xFFFFFFFF;
      unsigned char c;
      int res;
      int i;

   /* calculate CRC */
      sum = CRC32Accumulate(sum, 0x10);  

   /* get command */
      if ((res = GetByte(cmd)) != THPL_OK)
         return res;

   /* calculate CRC */
      sum = CRC32Accumulate(sum, *cmd);  

   /* get param #1 */
      if ((res = GetWord((unsigned long*) param1)) != THPL_OK)
         return res;

   /* calculate CRC */
      for (i = 0; i < 4; i++)
         sum = CRC32Accumulate(
            sum,
            (unsigned char) (((unsigned long)*param1 >> (i * 8)) & 0xFF)
         );  

   /* get param #2 */
      if ((res = GetWord((unsigned long*) param2)) != THPL_OK)
         return res;

   /* calculate CRC */
      for (i = 0; i < 4; i++)
         sum = CRC32Accumulate(
            sum,
            (unsigned char) (((unsigned long)*param2 >> (i * 8)) & 0xFF)
         );  

   /* get CRC from the packet */
      if ((res = GetWord(&crcRcvd)) != THPL_OK)
         return res;

   /* get tail of the message */
      if ((res = GetChar(&c)) != THPL_OK)
         return res; 
      
      if (c != 0x02)
         return THPL_INVALID_DATA;

      if (sum != crcRcvd)
         return THPL_INVALID_CRC;
         
      return THPL_OK;
   }

/*****************************************************************************
 *   Function: ReceiveLoadMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *             THPL_END_OF_DATA 
 *             THPL_INVALID_DATA 
 *             THPL_INVALID_CRC
 *   Globals:  
 *   Purpose:  This function shall receive the load message.
 *   Comments:    
 *****************************************************************************/

   static int ReceiveLoadMsg(void)
   {
      unsigned char *addr;
      unsigned char c, last[4]; 
      unsigned long sum = 0xFFFFFFFF;
      int res;
      int i;

   /* calculate CRC */
      sum = CRC32Accumulate(sum, 0x11);  

   /* get destination address */
      if ((res = GetWord((unsigned long*) &addr)) != THPL_OK)
         return res;

   /* calculate CRC */
      for (i = 0; i < 4; i++)
         sum = CRC32Accumulate(
            sum,
            (unsigned char) (((unsigned long) addr >> (i * 8)) & 0xFF)
         );  

   /* receive CRC if length of data is equal to 0, otherwise any byte of data */
      if ((res = GetByte(&last[3])) != THPL_OK ||
          (res = GetByte(&last[2])) != THPL_OK ||
          (res = GetByte(&last[1])) != THPL_OK ||    
          (res = GetByte(&last[0])) != THPL_OK)
      {
         return res;
      }

   /* get data */
      while ((res = GetByte(&c)) == THPL_OK)
      {
      /* calculate CRC of data */
         sum = CRC32Accumulate(sum, last[3]);  

      /* write data at the specified location */
         if ((res = THCLWriteByte(addr, &last[3])) != THCL_OK)
         {
            break;
         }

      /* move destination address */
         addr++;

      /* save currently read byte */
         last[3] = last[2]; 
         last[2] = last[1]; 
         last[1] = last[0]; 
         last[0] = c; 
      }
   
   /* is it the end of the message */
      if (res == THPL_END_OF_DATA)
      {
      /* the CRC of the message is incorrect */
         if (sum != (((unsigned long) last[3] << 24) +
                     ((unsigned long) last[2] << 16) +
                     ((unsigned long) last[1] << 8)  +
                     ((unsigned long) last[0] << 0)))
         {
         /* incorrect CRC */
            return THPL_INVALID_CRC;
         }

         return THPL_OK;
      }

      return res;
   }

/*****************************************************************************
 *   Function: ReceivePingMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *             THPL_END_OF_DATA 
 *             THPL_INVALID_DATA 
 *   Globals:  
 *   Purpose:  This function shall receive the ping message.
 *   Comments:    
 *****************************************************************************/

   static int ReceivePingMsg(void)
   {
	   unsigned char c;
      int res;
   	
   /* get tail of the message */
      if ((res = GetChar(&c)) != THPL_OK)
         return res;
      
      if (c != 0x02)
         return THPL_INVALID_DATA;
         
      return THPL_OK;
   }

/*****************************************************************************
 *   Function: SendDataMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT 
 *   Globals:  
 *   Purpose:  This function shall send the data message.
 *   Comments:    
 *****************************************************************************/

   static int SendDataMsg(
      unsigned char *addr,
      unsigned long len
   )
   {
      unsigned long i;
      unsigned char byte;
      int res;
      
   /* start sending of data message */
      if ((res = THPLStartDataMsg(addr)) != THPL_OK)
         return res;

      for (i = 0; i < len; i++)      
      {
      /* read byte from memory */
         if ((res = THCLReadByte(&addr[i], &byte)) != THCL_OK)
            return res;
         
      /* send the next byte of data */
         if ((res = THPLPutByteToMsg(byte)) != THPL_OK)
            return res;    
      }

   /* finish sending of data message */
      if ((res = THPLFinishDataMsg()) != THPL_OK)
         return res;

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLSendAckMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall send acknowledge message.
 *   Comments:    
 *****************************************************************************/

   int THPLSendAckMsg(int val)
   {
      int i;
      int res;
      unsigned long sum = 0xFFFFFFFF;

   /* send head of the message */
      if ((res = PutChar(0x01)) != THPL_OK)
         return res;

   /* send the message type */
      if ((res = PutChar(0x1A)) != THPL_OK)
         return res;
               
   /* calculate CRC */
      sum = CRC32Accumulate(sum, 0x1A);
               
   /* send a given value */
      if ((res = PutWord((unsigned long) val)) != THPL_OK)
         return res;
               
   /* calculate CRC */
      for (i = 0; i < 4; i++)
         sum = CRC32Accumulate(
            sum,
            (unsigned char) (((unsigned long)val >> (i * 8)) & 0xFF)
         );  
               
   /* send CRC */
      if ((res = PutWord(sum)) != THPL_OK)
         return res;
               
   /* send tail of the massage */
      if ((res = PutChar(0x02)) != THPL_OK)
         return res;

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLSendNackMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT 
  *   Globals:  
 *   Purpose:  This function shall send acknowledge message.
 *   Comments:    
 *****************************************************************************/

   int THPLSendNackMsg(int val)
   {
      int res, i;
      unsigned long sum = 0xFFFFFFFF;
      
   /* send head of the message */
      if ((res = PutChar(0x01)) != THPL_OK)
         return res;

   /* send the message type */
      if ((res = PutChar(0x1B)) != THPL_OK)
         return res;

   /* calculate CRC */
      sum = CRC32Accumulate(sum, 0x1B);

   /* send a given value */
      if ((res = PutWord((unsigned long) val)) != THPL_OK)
         return res;
               
   /* calculate CRC */
      for (i = 0; i < 4; i++)
         sum = CRC32Accumulate(
            sum,
            (unsigned char) (((unsigned long)val >> (i * 8)) & 0xFF)
         );  
               
   /* send CRC */
      if ((res = PutWord(sum)) != THPL_OK)
         return res;
               
   /* send tail of the massage */
      if ((res = PutChar(0x02)) != THPL_OK)
         return res;

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: THPLSendHelloMsg
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall send hello message.
 *   Comments:    
 *****************************************************************************/

   int THPLSendHelloMsg(void)
   {
      int res;
      
   /* send head of the message */
      if ((res = PutChar(0x01)) != THPL_OK)
         return res;

   /* send the message type */
      if ((res = PutChar(0x0F)) != THPL_OK)
         return res;
               
   /* send tail of the massage */
      if ((res = PutChar(0x02)) != THPL_OK)
         return res;

      return THPL_OK;
   }

/*****************************************************************************
 *   Function: GetChar
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT 
 *   Globals:  
 *   Purpose:  This function shall get character from a message.
 *   Comments:    
 *****************************************************************************/

   static int GetChar(
      unsigned char *c
   )
   {
      int res;
      
   /* get character directly with timeout */
      if ((res = THCLGetChar((char *)c, ioTimeout)) != THCL_OK)
         return res;

   /* save the last character */
      lastChar = *c;
      
      return THPL_OK;  
   }

/*****************************************************************************
 *   Function: GetByte
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *             THPL_END_OF_DATA 
 *             THPL_INVALID_DATA 
 *   Globals:  
 *   Purpose:  This function shall get byte from a message.
 *   Comments:    
 *****************************************************************************/

   static int GetByte(
      unsigned char *c
   )
   {
      unsigned char ch,cl;
      int res;

   /* get the first character */
      if ((res = GetChar(&ch)) != THPL_OK)
         return res;

   /* check character and convert it */
      if ((res = Bcd2Dec(ch, &ch)) != THPL_OK)
         return res;

   /* get the second character */
      if ((res = GetChar(&cl)) != THPL_OK)
         return res;

   /* check character and convert it */
      if ((res = Bcd2Dec(cl, &cl)) != THPL_OK)
         return res;

   /* calculate value of a byte */   
      *c = (ch << 4) + cl;

      return THPL_OK;  
   }

/*****************************************************************************
 *   Function: GetWord
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *             THPL_END_OF_DATA  
 *             THPL_INVALID_DATA 
 *   Globals:  
 *   Purpose:  This function shall get word from a message.
 *   Comments:    
 *****************************************************************************/

   static int GetWord(
      unsigned long *c
   )
   {
      unsigned char c3,c2,c1,c0;
      int res;

   /* get the first byte of a word */
      if ((res = GetByte(&c3)) != THPL_OK ||
          (res = GetByte(&c2)) != THPL_OK ||
          (res = GetByte(&c1)) != THPL_OK ||
          (res = GetByte(&c0)) != THPL_OK)
      {
         return res;
      }

   /* calculate value of a word */
      *c = (c3 << 24) + (c2 << 16) + (c1 << 8) + c0;

      return THPL_OK;  
   }

/*****************************************************************************
 *   Function: PutChar
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall put character to a message.
 *   Comments:    
 *****************************************************************************/

   static int PutChar(
      unsigned char c
   )
   {
      int res;
       
   /* put given character directly with timeout */
      if ((res = THCLPutChar(c, ioTimeout)) != THCL_OK)
         return res;

      return THPL_OK;  
   }

/*****************************************************************************
 *   Function: PutByte
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall put byte to a message.
 *   Comments:    
 *****************************************************************************/

   static int PutByte(
      unsigned char c
   )
   {
      int res;
      
   /* convert byte and put it */
      if ((res = PutChar(Dec2BcdHi(c))) != THPL_OK ||
          (res = PutChar(Dec2BcdLo(c))) != THPL_OK)
      {
         return res;
      }

      return THPL_OK;  
   }

/*****************************************************************************
 *   Function: PutWord
 *   Returns:  THPL_OK
 *             THPL_IO_ERROR
 *             THPL_IO_TIMEOUT
 *   Globals:  
 *   Purpose:  This function shall put word to a message.
 *   Comments:    
 *****************************************************************************/

   static int PutWord(
      unsigned long c
   )
   {
      int res;
      
   /* convert word and put it */
      if ((res = PutByte((unsigned char) (c >> 24) & 0xFF)) != THPL_OK ||
          (res = PutByte((unsigned char) (c >> 16) & 0xFF)) != THPL_OK ||
          (res = PutByte((unsigned char) (c >>  8) & 0xFF)) != THPL_OK ||
          (res = PutByte((unsigned char) (c >>  0) & 0xFF)) != THPL_OK)
      {
         return res;
      }

      return THPL_OK;  
   }

/*****************************************************************************
 *   Function: Bcd2Dec
 *   Returns:  THPL_OK
 *             THPL_INVALID_DATA
 *             THPL_END_OF_DATA  
 *   Globals:  
 *   Purpose:  This function shall convert BCD value to decimal value.
 *   Comments:    
 *****************************************************************************/

   static int Bcd2Dec(
      unsigned char bcd,
      unsigned char *c
   )
   {
      if (bcd >= '0' && bcd <= '9')
         *c = bcd - '0';
      else if (bcd >= 'A' && bcd <= 'F')
         *c = bcd - 'A' + 10;
      else if (bcd == 0x02)
         return THPL_END_OF_DATA;
      else
         return THPL_INVALID_DATA;

      return THPL_OK;  
   }

/*****************************************************************************
 *   Function: Dec2BcdLo
 *   Returns:  
 *   Globals:  
 *   Purpose:  This function shall convert the lowest 4 bits of byte to ASCII.
 *   Comments:    
 *****************************************************************************/

   static unsigned char Dec2BcdLo(
      unsigned char c
   )
   {
      char code[] = "0123456789ABCDEF";
      
   /* convert data and return new code */
      return code[c & 0x0F];  
   }

/*****************************************************************************
 *   Function: Dec2BcdHi
 *   Returns:  
 *   Globals:  
 *   Purpose:  This function shall convert the highest 4 bits of byte to ASCII.
 *   Comments:    
 *****************************************************************************/

   static unsigned char Dec2BcdHi(
      unsigned char c
   )
   {
      char code[] = "0123456789ABCDEF";
      
   /* convert data and return new code */
      return code[c >> 4];  
   }

#ifdef __cplusplus
}
#endif
