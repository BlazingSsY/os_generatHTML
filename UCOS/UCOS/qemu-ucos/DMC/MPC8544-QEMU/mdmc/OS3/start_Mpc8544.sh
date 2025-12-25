#!/bin/bash
home_dir="$HOME"

tmp_dir="$home_dir/tmp"

if [ ! -d "$tmp_dir" ]; then
    mkdir -p "$tmp_dir"
fi

QEMU_CMD="qemu-system-ppc -M ppce500 -cpu mpc8544e  -nographic -bios ../../../../build/u-boot -kernel ../../../../build/uImage -serial pty"
QEMU_DEBUG="qemu-system-ppc -M ppce500 -cpu mpc8544e -nographic -bios ../../../../build/u-boot -kernel ../../../../build/uImage -serial pty -serial mon:stdio -s -S"
QEMU_COV="qemu-system-ppc -M ppce500 -cpu mpc8544e  -nographic -bios ../../../../build/u-boot -kernel ../../../../build/uImage -plugin ./coverage_plugin/coverage_plugin.so -serial pty"
if [ "$1" == "debug" ]; then
	$QEMU_DEBUG > $tmp_dir/qemu_output.txt 2>&1 &
elif [ "$1" = "cover" ]; then
	$QEMU_COV > "$tmp_dir/qemu_output.txt" 2>&1 &
else
	$QEMU_CMD > $tmp_dir/qemu_output.txt 2>&1 &
fi

QEMU_PID=$!

sleep 5

grep "char device redirected to" $tmp_dir/qemu_output.txt | sed -n 's/.*char device redirected to \/dev\/pts\/\([0-9]*\).*/\/dev\/pts\/\1/p' > $tmp_dir/serial

echo "/dev/pts/* device extracted to /tmp/serial:"
cat $tmp_dir/serial

echo "QEMU is running with PID $QEMU_PID, press Ctrl+C to terminate this script..."
tail -f $tmp_dir/qemu_output.txt
