EXTRA_CFLAGS := -I$(src)/include
ccflags-y += -Wno-declaration-after-statement
ccflags-$(CONFIG_TMF882X_QCOM_AP) += -DCONFIG_TMF882X_QCOM_AP
obj-$(CONFIG_SENSORS_TMF882X) += tmf882x.o
tmf882x-y += tmf882x_driver.o tmf882x_clock_correction.o tmf882x_mode.o tmf882x_mode_app.o tmf882x_mode_bl.o tmf882x_interface.o intel_hex_interpreter.o
