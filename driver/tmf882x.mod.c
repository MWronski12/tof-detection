#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/export-internal.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif


static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x281823c5, "__kfifo_out_peek" },
	{ 0xd0e9fb09, "release_firmware" },
	{ 0x4d291584, "misc_deregister" },
	{ 0x833e8b97, "devm_request_threaded_irq" },
	{ 0xbf0dd6fb, "devm_kmalloc" },
	{ 0x5e515be6, "ktime_get_ts64" },
	{ 0xc358aaf8, "snprintf" },
	{ 0x8f678b07, "__stack_chk_guard" },
	{ 0xf23fcb99, "__kfifo_in" },
	{ 0xefd6cf06, "__aeabi_unwind_cpp_pr0" },
	{ 0xf9dd9922, "__init_swait_queue_head" },
	{ 0x963e0acd, "finish_wait" },
	{ 0x314b20c8, "scnprintf" },
	{ 0x1e02377d, "sysfs_remove_groups" },
	{ 0xe5ea3d4, "devm_input_allocate_device" },
	{ 0xfa5c565f, "sysfs_create_groups" },
	{ 0xa74d2d2c, "input_unregister_device" },
	{ 0x9d669763, "memcpy" },
	{ 0x37a0cba, "kfree" },
	{ 0xc3055d20, "usleep_range_state" },
	{ 0x93f6bff1, "prepare_to_wait_event" },
	{ 0xbb473bac, "gpiod_get_value" },
	{ 0x54bd70c, "devm_gpiod_get_optional" },
	{ 0xb3f7646e, "kthread_should_stop" },
	{ 0xa8f7cb55, "__wake_up" },
	{ 0x52e07b4d, "devm_gpiod_put" },
	{ 0x555c0f92, "of_get_property" },
	{ 0x16f30eda, "wake_up_process" },
	{ 0x96efa8de, "request_firmware_direct" },
	{ 0x87a10d5, "wait_for_completion_interruptible_timeout" },
	{ 0x92997ed8, "_printk" },
	{ 0x1000e51, "schedule" },
	{ 0x20903938, "input_register_device" },
	{ 0x3ea1b6e4, "__stack_chk_fail" },
	{ 0x5e7bf263, "devm_free_irq" },
	{ 0x6444b892, "_dev_info" },
	{ 0x800473f, "__cond_resched" },
	{ 0x7c6ce43b, "i2c_register_driver" },
	{ 0x49f26466, "kstrndup" },
	{ 0xfe487975, "init_wait_entry" },
	{ 0xbca1ff89, "_dev_err" },
	{ 0x6eb36404, "irq_get_irq_data" },
	{ 0xe8371cdf, "mutex_lock" },
	{ 0x365acda7, "set_normalized_timespec64" },
	{ 0x94b2e890, "kthread_stop" },
	{ 0xbcab6ee6, "sscanf" },
	{ 0x8a01a639, "__mutex_init" },
	{ 0x4578f528, "__kfifo_to_user" },
	{ 0x65929cae, "ns_to_timespec64" },
	{ 0x5f754e5a, "memset" },
	{ 0x7b26cef6, "_dev_warn" },
	{ 0x60620e5, "misc_register" },
	{ 0xe707d823, "__aeabi_uidiv" },
	{ 0xddece99e, "__init_waitqueue_head" },
	{ 0xbab36724, "input_event" },
	{ 0xdf98c806, "complete_all" },
	{ 0x193c3c66, "input_set_abs_params" },
	{ 0xefae4e96, "mutex_trylock" },
	{ 0x744c36a8, "kthread_create_on_node" },
	{ 0x85df9b6c, "strsep" },
	{ 0x7e423ba3, "mutex_unlock" },
	{ 0xb1ad28e0, "__gnu_mcount_nc" },
	{ 0xda1781a7, "i2c_transfer" },
	{ 0xe720a93a, "__wake_up_sync" },
	{ 0xe5633b20, "i2c_del_driver" },
	{ 0x42b57695, "gpiod_direction_output" },
	{ 0xc4f0da12, "ktime_get_with_offset" },
	{ 0x2d6fcc06, "__kmalloc" },
	{ 0xcaa72ffd, "module_layout" },
};

MODULE_INFO(depends, "");

MODULE_ALIAS("of:N*T*Cams,tmf882x");
MODULE_ALIAS("of:N*T*Cams,tmf882xC*");
MODULE_ALIAS("i2c:tmf882x");

MODULE_INFO(srcversion, "E65912D810C661AECD7BD79");
