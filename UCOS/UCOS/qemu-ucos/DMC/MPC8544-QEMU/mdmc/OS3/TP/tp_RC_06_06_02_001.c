/* Traceability Information
<FILE_NAME>     tp_RC_06_06_02_001.c
<SOURCE_FILE>   os_sem.c
<MODULE>        OSSemCreate
<VISIBILITY>    API
<HI_REQ>        RC.6.6.2
<LL_REQ>        RC.6.6.2-1
<MAX_TEST_CASE> 1
*/


#include  <cpu.h>
#include  <os.h>
#include  "app_cfg.h"
#include "verotrg.h"

void tp_RC_06_06_02_001(void)
{
    verHeader("tp_RC_06_06_02_001", "os_sem.c", "OSSemCreate", "RC.6.6.2-1", 1);

    /* <TEST_CASE> 1 */
    verTestCase(1);
    /* <REQ_NUM> RC.3.1.2.1-1 */
    verReqNum("RC.6.6.2-1");

    verExpected("OS_ERR_OBJ_PTR_NULL");

    OS_ERR  os_err = OS_ERR_OBJ_PTR_NULL;
    OS_SEM* p_sem = NULL;

    if (os_err == OS_ERR_OBJ_PTR_NULL)
    {
        verActual("OS_ERR_OBJ_PTR_NULL");
        verPassed(1);
    }
    else
    {
        verActual("FAILED");
        verFailed(1);
    }


    verSummary();
}

