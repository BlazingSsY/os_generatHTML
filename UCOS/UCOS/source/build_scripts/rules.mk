
# rules.library - Host independent rules for making libraries
#
# Copyright (c) 2024-2027 avic, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable avic license agreement.
#
# modification history
# --------------------
# 01a,16sept24,guqf   created
#
# DESCRIPTION
# This file is included by every Makefile in the run-time (not BSPs).
# This file contains makefile rules that are host independent for creating
# ucos libraries. It also contains implicit rules for .c .s .cpp and .cxx
# files in either the current directory or in $(LIBDIR).
#
# In each source directory, the list of source files is obtained and matched
# against the objects specified to be built in the OBJS macro. In this way 
# extraneous .c and .s files are ignored and make does not fail if it doesn't
# find the source file to an object in OBJS (This is the case with most source
# customers).
#
#
# If the macro SUBDIRS is defined with directories we build the subdirectories 
# before we build the current dir.
#
# INCLUDES

include $(PRJ_DIR)/build_script/defs.default

# implicit rules

.s.o :
	@ $(RM) $@
	$(CC) $(CFLAGS_AS) $(OPTION_OBJECT_ONLY) $(OPTION_OBJECT_NAME)$@ $<

.c.o :
	@ $(RM) $@
	$(CC) $(CFLAGS) $($(<:.c=)__CFLAGS) $(OPTION_OBJECT_ONLY) $<

# rules to build objects in $(LIBDIR)
$(LIBDIR)/%.o : %.c
	@ $(RM) $(subst /,$(DIRCHAR),$@)
	$(CC) $(CFLAGS) $($(<:.c=)__CFLAGS) $(OPTION_OBJECT_ONLY) $(OPTION_OBJECT_NAME)$@ $<


$(LIBDIR)/%.o : %.s
	@ $(RM) $(subst /,$(DIRCHAR),$@)
	$(CC) $(CFLAGS_AS) $(OPTION_OBJECT_ONLY) $(OPTION_OBJECT_NAME)$@ $<

# rules to build objects in $(LIBDIRWDBST)
$(LIBDIRWDBST)/%.o : %.c
	@ $(RM) $(subst /,$(DIRCHAR),$@)
	$(CC) $(CFLAGS) $(WDBST_CFLAGS) $($(<:.c=)__CFLAGS) \
		$(OPTION_OBJECT_ONLY) $(OPTION_OBJECT_NAME)$@ $<

$(LIBDIRWDBST)/%.o : %.s
	@ $(RM) $(subst /,$(DIRCHAR),$@)
	$(CC) $(CFLAGS_AS) $(WDBST_CFLAGS_AS) $(OPTION_OBJECT_ONLY) \
		$(OPTION_OBJECT_NAME)$@ $<

# rule for munchless C++ compiles
$(LIBDIR)/%.o : %.cpp
	@ $(RM) $(subst /,$(DIRCHAR),$@)
	$(CXX) $(C++FLAGS) $(OPTION_OBJECT_ONLY) $(OPTION_OBJECT_NAME)$@ $<

# Rule for standalone "munched" C++ modules.

# In general the only library modules that should be munched are 
# standalone test programs. Certainly nothing in the runtime should be 
# munched until BSP or Project build time. If you want your
# module to be munched, specify a .out target in $(OBJS) instead
# of a .o.
 
$(LIBDIR)/%.out : %.cpp
	@ $(RM) $@
	$(CXX) $(C++FLAGS) $(OPTION_OBJECT_ONLY) $(OPTION_OBJECT_NAME) \
      $(basename $@).o $<
	@ $(RM) ctdt.c
	$(NM) $(basename $@).o | $(MUNCH) > ctdt.c
	$(MAKE) CC_COMPILER="-fdollars-in-identifiers" ctdt.o
	$(LD) -r $(OPTION_OBJECT_NAME)$@ $(basename $@).o ctdt.o
	@ $(RM) $(basename $@).o ctdt.c ctdt.o

# rule for munchless C++ compiles
.cpp.o :
	@ $(RM) $@
	$(CXX) $(C++FLAGS) $(OPTION_OBJECT_ONLY) $<

.cxx.o :
	@ $(RM) $@
	$(CXX) $(C++FLAGS) $(OPTION_OBJECT_ONLY) $<

# C++ compile and munch
.cpp.out :
	@ $(RM) $@
	$(CXX) $(C++FLAGS) $(OPTION_OBJECT_ONLY) $<
	@ $(RM) $@ ctdt.c
	$(NM) $*.o | $(MUNCH) > ctdt.c
	$(MAKE) CC_COMPILER="-fdollars-in-identifiers" ctdt.o
	$(LD) -r $(OPTION_OBJECT_NAME)$@ $*.o ctdt.o
	@ $(RM) ctdt.c ctdt.o

.cxx.out :
	@ $(RM) $@
	$(CXX) $(C++FLAGS) $(OPTION_OBJECT_ONLY) $<
	@ $(RM) $@ ctdt.c
	$(NM) $*.o | $(MUNCH) > ctdt.c
	$(MAKE) CC_COMPILER="-fdollars-in-identifiers" ctdt.o
	$(LD) -r $(OPTION_OBJECT_NAME)$@ $*.o ctdt.o
	@ $(RM) ctdt.c ctdt.o

# rules to construct object lists

# vxWorks source distribution do not always have all of the
# sources to object files specified in macro OBJS macro.
# We use GNU make functions to find what we need to build

# get the list of .c, .cpp and .s files
FILE_LIST       = $(wildcard *.[cs]) $(wildcard *.cpp) $(INDIRECT_SOURCES)

# Change .c to .o in FILE_LIST and store in TMP_LIST
TMP_LIST        = $(FILE_LIST:.c=.o)

# Change .cpp to .o in TMP_LIST and store in TMP1_LIST
TMP1_LIST        = $(TMP_LIST:.cpp=.o)

# We can also build .out files from .cpp files
TMP2_LIST        = $(subst .cpp,.out,(filter %.cpp,$(FILE_LIST)))

# Change .s to .o in TMP1_LIST, concat with TMP2_LIST, and store in 
# OBJ_PRESENT. These are the objects we can build
OBJ_PRESENT     = $(TMP1_LIST:.s=.o) $(TMP2_LIST)

# Find the intersection of the objects we can build and the objects we'd
# like to build
OBJS_TO_BUILD		= $(filter $(OBJ_PRESENT),$(OBJS))
OBJS_WDBST_TO_BUILD	= $(filter $(OBJ_PRESENT),$(OBJS_WDBST))

#Now we fix up where they will go once they are built
LIBOBJS		= $(foreach file, $(OBJS_TO_BUILD), $(LIBDIR)/$(file))
LIBMETAOBJ	= $(foreach file, $(METAOBJ), $(LIBDIR)/$(file))
LIBOBJSWDBST	= $(foreach file, $(OBJS_WDBST_TO_BUILD), \
					$(LIBDIRWDBST)/$(file))

# It is safe to assume that if a subdirectory exists with a Makefile in it 
# that we want to build it. If this is not the case one needs to over ride 
# this definition in the Makefile for the directory in concern. 

# NOTE: to over ride this definition one must define SUBDIRS before the
# include directive for this file (rules.library) in the Makefile. To 
# exclude specific subdirs from the build, set EXCLUDE_SUBDIRS in your 
# environment before invoking 'make'
ifeq ($(SUBDIRS),)
ALL_SUBDIRS = $(patsubst %/,%,$(dir $(wildcard */Makefile)))
SUBDIRS_TMP = $(filter-out $(EXCLUDE_SUBDIRS), $(ALL_SUBDIRS))
SUBDIRS = $(filter-out $(UNSUPPORTED_SUBDIRS), $(SUBDIRS_TMP))
endif

Default: lib subdirs metaobj
ifneq ($(MAKETAIL),)
	($(MAKE) -f Makefile CPU=$(CPU) TOOL=$(TOOL)	\
	 $(MAKETAIL)					\
	 MAKETAIL='')				
endif

# recursive clean rule
rclean: 
ifneq ($(SUBDIRS),)
	$(MAKE) CPU=$(CPU) TOOL=$(TOOL) TGT_DIR=$(TGT_DIR) \
		TARGET=rclean $(SUBDIRS)
endif
	$(MAKE) CPU=$(CPU) TOOL=$(TOOL) TGT_DIR=$(TGT_DIR) clean
ifeq ($(CLEANLIBS),YES)
	$(RM) $(wildcard $(TGT_DIR)/lib/lib$(CPU)$(TOOL)*.a)
endif

# recursive build of all objects. The hope is that this rule will help
# with parallel builds. Calling lib and subdirs with parallel builds
# has the advers effect of trying to create libraries from mutilple
# subdirectories that tends to destroy the library.
all-objs : objs
ifneq ($(SUBDIRS),)
	$(MAKE) CPU=$(CPU) TOOL=$(TOOL) TGT_DIR=$(TGT_DIR) \
		TARGET=al-objs $(SUBDIRS)
endif

# Just in case you want to build objects and not update the archives
objs:	$(LIBOBJS)

# the metaobj rule will link a collection of objects into a single object
metaobj: $(LIBMETAOBJ)

ifneq ($(LIBMETAOBJ),)
$(LIBMETAOBJ): $(foreach file,$($(METAOBJ)_OBJS),$(LIBDIR)/$(file))
	$(LD) -r -o $@ $^
endif

release:
	$(MAKE) CPU=$(CPU) TOOL=$(TOOL) TGT_DIR=$(TGT_DIR) \
		TARGET=release

release-wdbst:
	$(MAKE) CPU=$(CPU) TOOL=$(TOOL) TGT_DIR=$(TGT_DIR) \
		TARGET="subdirs libwdbst"

include $(TGT_DIR)/h/make/rules-lib.$(WIND_HOST_TYPE)

# we don't need a dependency list if are not building objects
ifneq ($(OBJS),)

# We suppress the warning message about non existent file and setting of errno
# by prepending - . GNU make allows this.

-include depend.$(CPU)$(TOOL)

endif
