CFLAGS = -std=c99 -D__WIN32__ -g -DNO_TYPEDEF_OS_FLAGS  
CC = gcc

MINGW_LIB=/msys64/mingw64/lib/
#调试用目录设置
BUILD_DIR=/d/learn/UCOS-III-x86-win32/build


INCLUDE_DIR = -I$(CURDIR) \
          -I../../../../Micrium/software/uC-CPU \
		  -I../../../../Micrium/software/uC-CPU/Win32/Visual_Studio \
		  -I../../../../Micrium/software/uCOS-III/Source \
		  -I../../../../Microsoft/Windows/Kernel \
		  -I../../../../Micrium/software/uC-LIB \
		  -I../../../../Micrium/software/uCOS-III/Ports/Win32/Visual_Studio \    

SOURCES_C=os_app_hooks.c 
OBJECTS_C=$(patsubst %.c, $(BUILD_DIR)/%.o, $(SOURCES_C))



.PHONY: all uc-app clean always

all: uc-app

uc-app: $(BUILD_DIR)/uc-app.exe  

$(BUILD_DIR)/uc-app.exe: $(OBJECTS_C) $(BUILD_DIR)/main.o 
	gcc -g -D__WIN32__ -DNO_TYPEDEF_OS_FLAGS -o $@ $(BUILD_DIR)/main.o $(BUILD_DIR)/os_app_hooks.o \
	   $(BUILD_DIR)/uc-cpu.a $(BUILD_DIR)/uc-os.a $(BUILD_DIR)/uc-lib.a \
	-L$(MINGW_LIB) -lwinmm   


$(OBJECTS_C): $(SOURCES_C)
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) $(INCLUDE_DIR) -c -o $@ $<
	@echo "--> Compiled: " $<

$(BUILD_DIR)/main.o:main.c
	@$(CC) $(CFLAGS) $(INCLUDE_DIR) -c -o $@ $<

clean:
	@rm -f $(BUILD_DIR)/uc-lib.a