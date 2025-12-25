/* VerOCodeAPI.h   -   VerOCode Monitor API header file */

/* Copyright 2000-2007 Verocel, Inc. */

/*
modification history
--------------------
01f,10Jul2007,vti added vcmonProcessInterruptVectorTableUpdates()
01e,08Nov2006,vti added support for user-specified coverage tables
01d,03Apr2006,vti added vcmonGetVersionString().
01c,12Feb2006,vti added vcmonTransferResultsToBuffer().
01b,02Feb2006,vti added vcmonInitializeCoverageEx().
01a,12oct2004,vti created
*/

#ifndef __VEROCODE_MONITOR_API_H
#define __VEROCODE_MONITOR_API_H


#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */ 


/* typedefs */ 
typedef void (*VCMON_OUTPUT_CALLBACK_RTN)(char*);



/***************************************************************************
*
* vcmonInitializeCoverage - initialize coverage monitor
*
*/

extern void vcmonInitializeCoverage
   (
   void*    startAddress, /* coverage start address */
   int      size          /* actual size of the coverage data table in 1K blocks of words */
   );


/***************************************************************************
*
* vcmonInitializeCoverageEx - initialize coverage monitor - extended version
*
*/

extern void vcmonInitializeCoverageEx
   (
   void*    startAddress, /* coverage start address */
   void*    pDataTable,   /* address of the coverage data table; if NULL, use the built-in table */
   int      size,         /* actual size of the coverage data table in 1K blocks of words */
   int      expIndex,     /* when an instruction is executed, the monitor will update this */
                          /* instruction's coverage data only if (expIndex == *currIndex) */
   int*     pCurrIndex    /* physical address of 4-byte integer to be used by the monitor */
                          /* to extract the current value to be compared with <expIndex> */
   );
   

/***************************************************************************
*
* vcmonStartCoverage - start coverage 
*
*/

extern void vcmonStartCoverage (void);

  
/***************************************************************************
*
* vcmonStopCoverage - start coverage 
*
*/

extern void vcmonStopCoverage (void);


/***************************************************************************
*
* vcmonProcessInterruptVectorTableUpdates - tell the Monitor that the
*    software under test may have changed the interrupt vector table
*/

extern void vcmonProcessInterruptVectorTableUpdates (void);


/***************************************************************************
*
* vcmonTransferResults - transfer the resutls
*
*/

extern int vcmonTransferResults
    (
    int clear,         /* indicates whether the data table is to be cleared */
    VCMON_OUTPUT_CALLBACK_RTN outputcallback
                       /* callback routine called per coverage table row */
    );


/***************************************************************************
*
* vcmonTransferResultsToBuffer - transfer the results to buffer
*
*/

extern int vcmonTransferResultsToBuffer
   (
   int    clear, /* indicates whether the data table is to be cleared */
   void* buffer, /* address of buffer */
   int     size  /* size of buffer */
   );
   
   
/***************************************************************************
*
* vcmonGetVersionString - get monitor version string
*
*/

extern const char * vcmonGetVersionString
   (
   void
   );  
   

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* __VEROCODE_MONITOR_API_H */ 
