#!/bin/bash

CURRENT_DIR=$(pwd)
BSP_DIR=$CURRENT_DIR/../../../BSP
uCPU_DIR=$CURRENT_DIR/../../../../Micrium/Software/uC-CPU
uLIB_DIR=$CURRENT_DIR/../../../../Micrium/Software/uC-LIB
uCOS_DIR=$CURRENT_DIR/../../../../Micrium/Software/uCOS-III
chmod 777 ../../../../build/./mkimage
home_dir="$HOME"
tmp_dir="$home_dir/tmp"

if [ ! -d "$tmp_dir" ]; then
    mkdir -p "$tmp_dir"
fi

if [ "$1" == "rebuild" ]; then
    echo "Cleaning up previous build..."
    make clean

    ####################build BSP ##############################
    if [ ! -d "$BSP_DIR" ]; then
        echo "BSP directory does not exist: $BSP_DIR"
        exit 1
    fi

    echo "Executing make in BSP directory..."
    cd "$BSP_DIR"
    make clean
    make

    ####################build uC-CPU ##############################
    if [ ! -d "$uCPU_DIR" ]; then
        echo "uC-CPU directory does not exist: $uCPU_DIR"
        exit 1
    fi

    echo "Executing make in uC-CPU directory..."
    cd "$uCPU_DIR"
    make clean
    make

   ####################build uC-LIB ##############################
    if [ ! -d "$uLIB_DIR" ]; then
        echo "uC-LIB directory does not exist: $uLIB_DIR"
        exit 1
    fi

    echo "Executing make in uC-LIB directory..."
    cd "$uLIB_DIR"
    make clean
    make

   ####################build uC-LIB ##############################
    if [ ! -d "$uCOS_DIR" ]; then
        echo "uCOS-III directory does not exist: $uCOS_DIR"
        exit 1
    fi

    echo "Executing make in uCOS-III directory..."
    cd "$uCOS_DIR"
    make clean
    make
 
fi

cd "$CURRENT_DIR"
echo "Start to build ucos image"
make
cp "$CURRENT_DIR/../../../../build/bootApp.map" $tmp_dir/

