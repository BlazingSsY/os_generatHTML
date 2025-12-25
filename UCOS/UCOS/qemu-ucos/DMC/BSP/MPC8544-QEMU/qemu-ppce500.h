/*
 * Copyright 2011-2014 Freescale Semiconductor, Inc.
 *
 * SPDX-License-Identifier:	GPL-2.0+
 */

/*
 * Corenet DS style board configuration file
 */
#ifndef __QEMU_PPCE500_H
#define __QEMU_PPCE500_H

#define CONFIG_CMD_REGINFO

/* High Level Configuration Options */
#define CONFIG_BOOKE
#define CONFIG_E500			/* BOOKE e500 family */
#define CONFIG_QEMU_E500

#undef CONFIG_SYS_TEXT_BASE
#define CONFIG_SYS_TEXT_BASE	0xf01000 /* 15 MB */
#define CONFIG_SYS_GENERIC_BOARD

#define CONFIG_SYS_MPC85XX_NO_RESETVEC

#define CONFIG_SYS_RAMBOOT

#define CONFIG_PCI			/* Enable PCI/PCIE */
#define CONFIG_PCI1		1	/* PCI controller 1 */
#define CONFIG_FSL_PCI_INIT		/* Use common FSL init code */
#define CONFIG_SYS_PCI_64BIT		/* enable 64-bit PCI resources */

#define CONFIG_ENV_OVERWRITE

#define CONFIG_ENABLE_36BIT_PHYS

#define CONFIG_ADDR_MAP
#define CONFIG_SYS_NUM_ADDR_MAP		16	/* number of TLB1 entries */

#define CONFIG_SYS_MEMTEST_START	0x00200000	/* memtest works on */
#define CONFIG_SYS_MEMTEST_END		0x00400000
#define CONFIG_SYS_ALT_MEMTEST
#define CONFIG_PANIC_HANG	/* do not reset board on panic */

/* Needed to fill the ccsrbar pointer */
#define CONFIG_BOARD_EARLY_INIT_F

/* Virtual address to CCSRBAR */
#define CONFIG_SYS_CCSRBAR		0xe0000000
/* Physical address should be a function call */
#ifndef __ASSEMBLY__
extern unsigned long long get_phys_ccsrbar_addr_early(void);
#define CONFIG_SYS_CCSRBAR_PHYS_HIGH (get_phys_ccsrbar_addr_early() >> 32)
#define CONFIG_SYS_CCSRBAR_PHYS_LOW get_phys_ccsrbar_addr_early()
#else
#define CONFIG_SYS_CCSRBAR_PHYS_HIGH 0x0
#define CONFIG_SYS_CCSRBAR_PHYS_LOW CONFIG_SYS_CCSRBAR
#endif

#define CONFIG_PHYS_64BIT

/* Virtual address range for PCI region maps */
#define CONFIG_SYS_PCI_MAP_START	0x80000000
#define CONFIG_SYS_PCI_MAP_END		0xe8000000

/* Virtual address to a temporary map if we need it (max 128MB) */
#define CONFIG_SYS_TMPVIRT		0xe8000000

/*
 * DDR Setup
 */
#define CONFIG_VERY_BIG_RAM
#define CONFIG_SYS_DDR_SDRAM_BASE	0x00000000
#define CONFIG_SYS_SDRAM_BASE		CONFIG_SYS_DDR_SDRAM_BASE

#define CONFIG_CHIP_SELECTS_PER_CTRL	0

#define CONFIG_SYS_CLK_FREQ        33000000

#define CONFIG_SYS_NO_FLASH

#define CONFIG_SYS_BOOT_BLOCK		0x00000000	/* boot TLB */

#define CONFIG_SYS_MONITOR_BASE		CONFIG_SYS_TEXT_BASE

#define CONFIG_ENV_IS_NOWHERE

#define CONFIG_HWCONFIG

#define CONFIG_SYS_INIT_RAM_ADDR		0x00100000
#define CONFIG_SYS_INIT_RAM_ADDR_PHYS_HIGH	0x0
#define CONFIG_SYS_INIT_RAM_ADDR_PHYS_LOW	0x00100000
/* The assembler doesn't like typecast */
#define CONFIG_SYS_INIT_RAM_ADDR_PHYS \
	((CONFIG_SYS_INIT_RAM_ADDR_PHYS_HIGH * 1ull << 32) | \
	  CONFIG_SYS_INIT_RAM_ADDR_PHYS_LOW)
#define CONFIG_SYS_INIT_RAM_SIZE		0x00004000

#define CONFIG_SYS_GBL_DATA_OFFSET	(CONFIG_SYS_INIT_RAM_SIZE - \
					GENERATED_GBL_DATA_SIZE)
#define CONFIG_SYS_INIT_SP_OFFSET	CONFIG_SYS_GBL_DATA_OFFSET

#define CONFIG_SYS_MONITOR_LEN		(512 * 1024)
#define CONFIG_SYS_MALLOC_LEN		(4 * 1024 * 1024)

#define CONFIG_CONS_INDEX	1
#define CONFIG_SYS_NS16550
#define CONFIG_SYS_NS16550_SERIAL
#define CONFIG_SYS_NS16550_REG_SIZE	1
#define CONFIG_SYS_NS16550_CLK		(get_bus_freq(0))

#define CONFIG_SYS_BAUDRATE_TABLE	\
	{300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200}

#define CONFIG_SYS_NS16550_COM1	(CONFIG_SYS_CCSRBAR+0x4500)
#define CONFIG_SYS_NS16550_COM2	(CONFIG_SYS_CCSRBAR+0x4600)

/* Use the HUSH parser */
#define CONFIG_SYS_HUSH_PARSER
#define CONFIG_SYS_PROMPT_HUSH_PS2 "> "

/* pass open firmware flat tree */
#define CONFIG_OF_LIBFDT
#define CONFIG_OF_BOARD_SETUP
#define CONFIG_OF_STDOUT_VIA_ALIAS

/* new uImage format support */
#define CONFIG_FIT
#define CONFIG_FIT_VERBOSE	/* enable fit_format_{error,warning}() */

/*
 * General PCI
 * Memory space is mapped 1-1, but I/O space must start from 0.
 */

#ifdef CONFIG_PCI
#define CONFIG_PCI_INDIRECT_BRIDGE
#define CONFIG_PCI_PNP			/* do pci plug-and-play */

#define CONFIG_PCI_SCAN_SHOW		/* show pci devices on startup */
#define CONFIG_DOS_PARTITION
#endif	/* CONFIG_PCI */

#define CONFIG_LBA48
#define CONFIG_DOS_PARTITION
#define CONFIG_CMD_EXT2

/*
 * PIC
 */
#define MPC85xx_PICGCR_RST	0x80000000
#define MPC85xx_PICGCR_M	0x20000000
#define CONFIG_SYS_IMMR 0xe0000000
#define CFG_SYS_MPC85xx_PIC_OFFSET		0x40000


/*
 * __xx is ok: it doesn't pollute the POSIX namespace. Use these in the
 * header files exported to user space
 */


typedef __signed__ char __s8;
typedef unsigned char __u8;

typedef __signed__ short __s16;
typedef unsigned short __u16;

typedef __signed__ int __s32;
typedef unsigned int __u32;
typedef __signed__ char __s8;
typedef unsigned char __u8;

typedef __signed__ short __s16;
typedef unsigned short __u16;

typedef __signed__ int __s32;
typedef unsigned int __u32;

#ifdef __GNUC__
__extension__ typedef __signed__ long long __s64;
__extension__ typedef unsigned long long __u64;
#else
typedef __signed__ long long __s64;
typedef unsigned long long __u64;
#endif

typedef __s8  s8;
typedef __u8  u8;
typedef __s16 s16;
typedef __u16 u16;
typedef __s32 s32;
typedef __u32 u32;
typedef __s64 s64;
typedef __u64 u64;



/* PIC Registers */
typedef struct ccsr_pic {
	u8	res1[64];
	u32	ipidr0;		/* Interprocessor IRQ Dispatch 0 */
	u8	res2[12];
	u32	ipidr1;		/* Interprocessor IRQ Dispatch 1 */
	u8	res3[12];
	u32	ipidr2;		/* Interprocessor IRQ Dispatch 2 */
	u8	res4[12];
	u32	ipidr3;		/* Interprocessor IRQ Dispatch 3 */
	u8	res5[12];
	u32	ctpr;		/* Current Task Priority */
	u8	res6[12];
	u32	whoami;		/* Who Am I */
	u8	res7[12];
	u32	iack;		/* IRQ Acknowledge */
	u8	res8[12];
	u32	eoi;		/* End Of IRQ */
	u8	res9[3916];
	u32	frr;		/* Feature Reporting */
	u8	res10[28];
	u32	gcr;		/* Global Configuration */
#define MPC85xx_PICGCR_RST	0x80000000
#define MPC85xx_PICGCR_M	0x20000000
	u8	res11[92];
	u32	vir;		/* Vendor Identification */
	u8	res12[12];
	u32	pir;		/* Processor Initialization */
	u8	res13[12];
	u32	ipivpr0;	/* IPI Vector/Priority 0 */
	u8	res14[12];
	u32	ipivpr1;	/* IPI Vector/Priority 1 */
	u8	res15[12];
	u32	ipivpr2;	/* IPI Vector/Priority 2 */
	u8	res16[12];
	u32	ipivpr3;	/* IPI Vector/Priority 3 */
	u8	res17[12];
	u32	svr;		/* Spurious Vector */
	u8	res18[12];
	u32	tfrr;		/* Timer Frequency Reporting */
	u8	res19[12];
	u32	gtccr0;		/* Global Timer Current Count 0 */
	u8	res20[12];
	u32	gtbcr0;		/* Global Timer Base Count 0 */
	u8	res21[12];
	u32	gtvpr0;		/* Global Timer Vector/Priority 0 */
	u8	res22[12];
	u32	gtdr0;		/* Global Timer Destination 0 */
	u8	res23[12];
	u32	gtccr1;		/* Global Timer Current Count 1 */
	u8	res24[12];
	u32	gtbcr1;		/* Global Timer Base Count 1 */
	u8	res25[12];
	u32	gtvpr1;		/* Global Timer Vector/Priority 1 */
	u8	res26[12];
	u32	gtdr1;		/* Global Timer Destination 1 */
	u8	res27[12];
	u32	gtccr2;		/* Global Timer Current Count 2 */
	u8	res28[12];
	u32	gtbcr2;		/* Global Timer Base Count 2 */
	u8	res29[12];
	u32	gtvpr2;		/* Global Timer Vector/Priority 2 */
	u8	res30[12];
	u32	gtdr2;		/* Global Timer Destination 2 */
	u8	res31[12];
	u32	gtccr3;		/* Global Timer Current Count 3 */
	u8	res32[12];
	u32	gtbcr3;		/* Global Timer Base Count 3 */
	u8	res33[12];
	u32	gtvpr3;		/* Global Timer Vector/Priority 3 */
	u8	res34[12];
	u32	gtdr3;		/* Global Timer Destination 3 */
	u8	res35[268];
	u32	tcr;		/* Timer Control */
	u8	res36[12];
	u32	irqsr0;		/* IRQ_OUT Summary 0 */
	u8	res37[12];
	u32	irqsr1;		/* IRQ_OUT Summary 1 */
	u8	res38[12];
	u32	cisr0;		/* Critical IRQ Summary 0 */
	u8	res39[12];
	u32	cisr1;		/* Critical IRQ Summary 1 */
	u8	res40[188];
	u32	msgr0;		/* Message 0 */
	u8	res41[12];
	u32	msgr1;		/* Message 1 */
	u8	res42[12];
	u32	msgr2;		/* Message 2 */
	u8	res43[12];
	u32	msgr3;		/* Message 3 */
	u8	res44[204];
	u32	mer;		/* Message Enable */
	u8	res45[12];
	u32	msr;		/* Message Status */
	u8	res46[60140];
	u32	eivpr0;		/* External IRQ Vector/Priority 0 */
	u8	res47[12];
	u32	eidr0;		/* External IRQ Destination 0 */
	u8	res48[12];
	u32	eivpr1;		/* External IRQ Vector/Priority 1 */
	u8	res49[12];
	u32	eidr1;		/* External IRQ Destination 1 */
	u8	res50[12];
	u32	eivpr2;		/* External IRQ Vector/Priority 2 */
	u8	res51[12];
	u32	eidr2;		/* External IRQ Destination 2 */
	u8	res52[12];
	u32	eivpr3;		/* External IRQ Vector/Priority 3 */
	u8	res53[12];
	u32	eidr3;		/* External IRQ Destination 3 */
	u8	res54[12];
	u32	eivpr4;		/* External IRQ Vector/Priority 4 */
	u8	res55[12];
	u32	eidr4;		/* External IRQ Destination 4 */
	u8	res56[12];
	u32	eivpr5;		/* External IRQ Vector/Priority 5 */
	u8	res57[12];
	u32	eidr5;		/* External IRQ Destination 5 */
	u8	res58[12];
	u32	eivpr6;		/* External IRQ Vector/Priority 6 */
	u8	res59[12];
	u32	eidr6;		/* External IRQ Destination 6 */
	u8	res60[12];
	u32	eivpr7;		/* External IRQ Vector/Priority 7 */
	u8	res61[12];
	u32	eidr7;		/* External IRQ Destination 7 */
	u8	res62[12];
	u32	eivpr8;		/* External IRQ Vector/Priority 8 */
	u8	res63[12];
	u32	eidr8;		/* External IRQ Destination 8 */
	u8	res64[12];
	u32	eivpr9;		/* External IRQ Vector/Priority 9 */
	u8	res65[12];
	u32	eidr9;		/* External IRQ Destination 9 */
	u8	res66[12];
	u32	eivpr10;	/* External IRQ Vector/Priority 10 */
	u8	res67[12];
	u32	eidr10;		/* External IRQ Destination 10 */
	u8	res68[12];
	u32	eivpr11;	/* External IRQ Vector/Priority 11 */
	u8	res69[12];
	u32	eidr11;		/* External IRQ Destination 11 */
	u8	res70[140];
	u32	iivpr0;		/* Internal IRQ Vector/Priority 0 */
	u8	res71[12];
	u32	iidr0;		/* Internal IRQ Destination 0 */
	u8	res72[12];
	u32	iivpr1;		/* Internal IRQ Vector/Priority 1 */
	u8	res73[12];
	u32	iidr1;		/* Internal IRQ Destination 1 */
	u8	res74[12];
	u32	iivpr2;		/* Internal IRQ Vector/Priority 2 */
	u8	res75[12];
	u32	iidr2;		/* Internal IRQ Destination 2 */
	u8	res76[12];
	u32	iivpr3;		/* Internal IRQ Vector/Priority 3 */
	u8	res77[12];
	u32	iidr3;		/* Internal IRQ Destination 3 */
	u8	res78[12];
	u32	iivpr4;		/* Internal IRQ Vector/Priority 4 */
	u8	res79[12];
	u32	iidr4;		/* Internal IRQ Destination 4 */
	u8	res80[12];
	u32	iivpr5;		/* Internal IRQ Vector/Priority 5 */
	u8	res81[12];
	u32	iidr5;		/* Internal IRQ Destination 5 */
	u8	res82[12];
	u32	iivpr6;		/* Internal IRQ Vector/Priority 6 */
	u8	res83[12];
	u32	iidr6;		/* Internal IRQ Destination 6 */
	u8	res84[12];
	u32	iivpr7;		/* Internal IRQ Vector/Priority 7 */
	u8	res85[12];
	u32	iidr7;		/* Internal IRQ Destination 7 */
	u8	res86[12];
	u32	iivpr8;		/* Internal IRQ Vector/Priority 8 */
	u8	res87[12];
	u32	iidr8;		/* Internal IRQ Destination 8 */
	u8	res88[12];
	u32	iivpr9;		/* Internal IRQ Vector/Priority 9 */
	u8	res89[12];
	u32	iidr9;		/* Internal IRQ Destination 9 */
	u8	res90[12];
	u32	iivpr10;	/* Internal IRQ Vector/Priority 10 */
	u8	res91[12];
	u32	iidr10;		/* Internal IRQ Destination 10 */
	u8	res92[12];
	u32	iivpr11;	/* Internal IRQ Vector/Priority 11 */
	u8	res93[12];
	u32	iidr11;		/* Internal IRQ Destination 11 */
	u8	res94[12];
	u32	iivpr12;	/* Internal IRQ Vector/Priority 12 */
	u8	res95[12];
	u32	iidr12;		/* Internal IRQ Destination 12 */
	u8	res96[12];
	u32	iivpr13;	/* Internal IRQ Vector/Priority 13 */
	u8	res97[12];
	u32	iidr13;		/* Internal IRQ Destination 13 */
	u8	res98[12];
	u32	iivpr14;	/* Internal IRQ Vector/Priority 14 */
	u8	res99[12];
	u32	iidr14;		/* Internal IRQ Destination 14 */
	u8	res100[12];
	u32	iivpr15;	/* Internal IRQ Vector/Priority 15 */
	u8	res101[12];
	u32	iidr15;		/* Internal IRQ Destination 15 */
	u8	res102[12];
	u32	iivpr16;	/* Internal IRQ Vector/Priority 16 */
	u8	res103[12];
	u32	iidr16;		/* Internal IRQ Destination 16 */
	u8	res104[12];
	u32	iivpr17;	/* Internal IRQ Vector/Priority 17 */
	u8	res105[12];
	u32	iidr17;		/* Internal IRQ Destination 17 */
	u8	res106[12];
	u32	iivpr18;	/* Internal IRQ Vector/Priority 18 */
	u8	res107[12];
	u32	iidr18;		/* Internal IRQ Destination 18 */
	u8	res108[12];
	u32	iivpr19;	/* Internal IRQ Vector/Priority 19 */
	u8	res109[12];
	u32	iidr19;		/* Internal IRQ Destination 19 */
	u8	res110[12];
	u32	iivpr20;	/* Internal IRQ Vector/Priority 20 */
	u8	res111[12];
	u32	iidr20;		/* Internal IRQ Destination 20 */
	u8	res112[12];
	u32	iivpr21;	/* Internal IRQ Vector/Priority 21 */
	u8	res113[12];
	u32	iidr21;		/* Internal IRQ Destination 21 */
	u8	res114[12];
	u32	iivpr22;	/* Internal IRQ Vector/Priority 22 */
	u8	res115[12];
	u32	iidr22;		/* Internal IRQ Destination 22 */
	u8	res116[12];
	u32	iivpr23;	/* Internal IRQ Vector/Priority 23 */
	u8	res117[12];
	u32	iidr23;		/* Internal IRQ Destination 23 */
	u8	res118[12];
	u32	iivpr24;	/* Internal IRQ Vector/Priority 24 */
	u8	res119[12];
	u32	iidr24;		/* Internal IRQ Destination 24 */
	u8	res120[12];
	u32	iivpr25;	/* Internal IRQ Vector/Priority 25 */
	u8	res121[12];
	u32	iidr25;		/* Internal IRQ Destination 25 */
	u8	res122[12];
	u32	iivpr26;	/* Internal IRQ Vector/Priority 26 */
	u8	res123[12];
	u32	iidr26;		/* Internal IRQ Destination 26 */
	u8	res124[12];
	u32	iivpr27;	/* Internal IRQ Vector/Priority 27 */
	u8	res125[12];
	u32	iidr27;		/* Internal IRQ Destination 27 */
	u8	res126[12];
	u32	iivpr28;	/* Internal IRQ Vector/Priority 28 */
	u8	res127[12];
	u32	iidr28;		/* Internal IRQ Destination 28 */
	u8	res128[12];
	u32	iivpr29;	/* Internal IRQ Vector/Priority 29 */
	u8	res129[12];
	u32	iidr29;		/* Internal IRQ Destination 29 */
	u8	res130[12];
	u32	iivpr30;	/* Internal IRQ Vector/Priority 30 */
	u8	res131[12];
	u32	iidr30;		/* Internal IRQ Destination 30 */
	u8	res132[12];
	u32	iivpr31;	/* Internal IRQ Vector/Priority 31 */
	u8	res133[12];
	u32	iidr31;		/* Internal IRQ Destination 31 */
	u8	res134[4108];
	u32	mivpr0;		/* Messaging IRQ Vector/Priority 0 */
	u8	res135[12];
	u32	midr0;		/* Messaging IRQ Destination 0 */
	u8	res136[12];
	u32	mivpr1;		/* Messaging IRQ Vector/Priority 1 */
	u8	res137[12];
	u32	midr1;		/* Messaging IRQ Destination 1 */
	u8	res138[12];
	u32	mivpr2;		/* Messaging IRQ Vector/Priority 2 */
	u8	res139[12];
	u32	midr2;		/* Messaging IRQ Destination 2 */
	u8	res140[12];
	u32	mivpr3;		/* Messaging IRQ Vector/Priority 3 */
	u8	res141[12];
	u32	midr3;		/* Messaging IRQ Destination 3 */
	u8	res142[59852];
	u32	ipi0dr0;	/* Processor 0 Interprocessor IRQ Dispatch 0 */
	u8	res143[12];
	u32	ipi0dr1;	/* Processor 0 Interprocessor IRQ Dispatch 1 */
	u8	res144[12];
	u32	ipi0dr2;	/* Processor 0 Interprocessor IRQ Dispatch 2 */
	u8	res145[12];
	u32	ipi0dr3;	/* Processor 0 Interprocessor IRQ Dispatch 3 */
	u8	res146[12];
	u32	ctpr0;		/* Current Task Priority for Processor 0 */
	u8	res147[12];
	u32	whoami0;	/* Who Am I for Processor 0 */
	u8	res148[12];
	u32	iack0;		/* IRQ Acknowledge for Processor 0 */
	u8	res149[12];
	u32	eoi0;		/* End Of IRQ for Processor 0 */
	u8	res150[130892];
} ccsr_pic_t;

#define CFG_SYS_MPC8xxx_PIC_ADDR \
	(CONFIG_SYS_IMMR + CFG_SYS_MPC85xx_PIC_OFFSET)

/*
 * Environment
 */
#define CONFIG_ENV_SIZE		0x2000

#define CONFIG_LOADS_ECHO		/* echo on for serial download */

#define CONFIG_LAST_STAGE_INIT

/*
 * Command line configuration.
 */
#define CONFIG_CMD_DHCP
#define CONFIG_CMD_ELF
#define CONFIG_CMD_BOOTZ
#define CONFIG_CMD_GREPENV
#define CONFIG_CMD_IRQ
#define CONFIG_CMD_PING

#ifdef CONFIG_PCI
#define CONFIG_CMD_PCI
#endif

/*
 * Miscellaneous configurable options
 */
#define CONFIG_SYS_LONGHELP			/* undef to save memory	*/
#define CONFIG_CMDLINE_EDITING			/* Command-line editing */
#define CONFIG_AUTO_COMPLETE			/* add autocompletion support */
#define CONFIG_SYS_LOAD_ADDR	0x2000000	/* default load address */
#define CONFIG_SYS_CBSIZE	256		/* Console I/O Buffer Size */
#define CONFIG_SYS_PBSIZE (CONFIG_SYS_CBSIZE+sizeof(CONFIG_SYS_PROMPT)+16)
#define CONFIG_SYS_MAXARGS	16		/* max number of command args */
#define CONFIG_SYS_BARGSIZE	CONFIG_SYS_CBSIZE/* Boot Argument Buffer Size */

/*
 * For booting Linux, the board info and command line data
 * have to be in the first 64 MB of memory, since this is
 * the maximum mapped by the Linux kernel during initialization.
 */
#define CONFIG_SYS_BOOTMAPSZ	(64 << 20)	/* Initial map for Linux*/
#define CONFIG_SYS_BOOTM_LEN	(64 << 20)	/* Increase max gunzip size */

/*
 * Environment Configuration
 */
#define CONFIG_ROOTPATH		"/opt/nfsroot"
#define CONFIG_BOOTFILE		"uImage"
#define CONFIG_UBOOTPATH	"u-boot.bin"	/* U-Boot image on TFTP server*/

/* default location for tftp and bootm */
#define CONFIG_LOADADDR		1000000

#define CONFIG_BAUDRATE	115200

#define CONFIG_BOOTDELAY        1
#define CONFIG_BOOTCOMMAND		\
	"test -n \"$qemu_kernel_addr\" && bootm $qemu_kernel_addr - $fdt_addr_r\0"

#endif	/* __QEMU_PPCE500_H */
