    .globl  InsertFunC_A
    .globl  InsertFunC_B
    .globl  InsertFunC_C
    .globl  InsertFunC_D
    .globl  InsertFunC_E
    .globl  InsertFunC_F
    .globl  InsertFunC_G
    .globl  InsertFunC_H
    .globl  InsertFunC_I
    .globl  InsertFunC_J
    .section .text
    .align 4

InsertFunC_A:
    #lis     r5, tmp_record@h          # 加载sum地址的高位
    #ori     r5, r5, tmp_record@l       # 加载sum地址的低位
    #li      r6, 33              # 要写入的值
    #stw     r6, 0(r5)           # sum = 33
    #bl      insertFunc
    #b       asm_trampoline


    #mflr    r30    # 将LR（指向if语句）保存到r31
    #stwu    sp, -16(sp)        # 分配16字节栈空间
    #stw     r30, 12(sp)        # 将r30（即返回地址）保存到栈上
    #bl      custFunctionA         # 调用函数。这会修改LR，但没关系
    #lwz     r30, 12(sp)        # 从栈上恢复r31的值（真正的返回地址）
    #addi    sp, sp, 16         # 恢复栈指针
    #mtlr    r30                # 【最关键一步】将真正的返回地址放回LR
    #b       asm_trampoline_slotA     # 跳转到蹦床

    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionA  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotA   #跳到蹦床

InsertFunC_B:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionB  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotB   #跳到蹦床

InsertFunC_C:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionC  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotC   #跳到蹦床

InsertFunC_D:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionD  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotD   #跳到蹦床

InsertFunC_E:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionE  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotE   #跳到蹦床


InsertFunC_F:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionF  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotF   #跳到蹦床

InsertFunC_G:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionG  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotG   #跳到蹦床


InsertFunC_H:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionH  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotH   #跳到蹦床

InsertFunC_I:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionI  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotI     # 跳转到蹦床


InsertFunC_J:
    stwu    sp, -32(sp)    # 分配16字节栈空间
    stw     r30, 28(sp)    # 将原始的r30的值保存在sp + 28
    mflr    r30            # 将LR（指向if语句）保存到r320
    stw     r30, 24(sp)    # 将r30（原始LR）保存到栈上 sp + 24
    bl      custFunctionJ  
    lwz     r30, 24(sp)    # 从栈上恢复原始LR到r30
    mtlr    r30            # 将r30的值写入LR
    lwz     r30, 28(sp)    # 从栈上恢复原始r30值
    addi    sp, sp, 32     # 恢复栈指针
    b       asm_trampoline_slotJ   #跳到蹦床

