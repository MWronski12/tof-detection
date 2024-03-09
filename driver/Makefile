ifneq ($(KERNELRELEASE),)
#kbuild part of Makefile
include Kbuild
else
#normal Makefile
all:
	$(MAKE) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) -C $(LINUX_SRC) M=$$PWD modules EXTRA_CFLAGS="-I/home/szekler/tmf882x/include -I/usr/include/linux -I/usr/lib/gcc/arm-linux-gnueabihf/10/include"

modules:
	$(MAKE) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) -C $(LINUX_SRC) M=$$PWD $@

sign:
	$(SIGN_SCRIPT) sha512 $(LINUX_SRC)/signing_key.priv $(LINUX_SRC)/signing_key.x509 $(DEVICE_NAME).ko

clean:
	$(MAKE) -C $(LINUX_SRC) M=$$PWD clean

endif
