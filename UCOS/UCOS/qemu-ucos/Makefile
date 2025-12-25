all:
	make -C Micrium/Software/uC-CPU 
	make -C DMC/BSP
	make -C Micrium/Software/uCOS-III
	make -C Micrium/Software/uC-LIB
	make -C DMC/MPC8544-QEMU/mdmc/OS3
debug:
	qemu-system-ppc -M ppce500 -nographic -bios build/u-boot -kernel build/uImage -serial mon:stdio -s -S