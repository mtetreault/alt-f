#############################################################
#
# nbd (client only)
#
#############################################################

NBD_VERSION=2.9.11
NBD_SOURCE=nbd-$(NBD_VERSION).tar.bz2
NBD_CAT:=$(BZCAT)
NBD_SITE=$(BR2_SOURCEFORGE_MIRROR)/sourceforge/nbd/
NBD_DIR=$(BUILD_DIR)/nbd-$(NBD_VERSION)

$(DL_DIR)/$(NBD_SOURCE):
	$(call DOWNLOAD,$(NBD_SITE),$(NBD_SOURCE))

$(NBD_DIR)/.unpacked: $(DL_DIR)/$(NBD_SOURCE)
	$(NBD_CAT) $(DL_DIR)/$(NBD_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(NBD_DIR)/.configured: $(NBD_DIR)/.unpacked
	(cd $(NBD_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		CC=$(TARGET_CC) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
	)
	touch $@

$(NBD_DIR)/nbd-client: $(NBD_DIR)/.configured
	$(MAKE) -C $(NBD_DIR) nbd-client

$(TARGET_DIR)/sbin/nbd-client: $(NBD_DIR)/nbd-client
	cp $< $@
	$(STRIPCMD) $@

nbd: uclibc libglib2 $(TARGET_DIR)/sbin/nbd-client

nbd-source: $(DL_DIR)/$(NBD_SOURCE)

nbd-clean:
	rm -f $(TARGET_DIR)/sbin/nbd-client
	-$(MAKE) -C $(NBD_DIR) clean

nbd-dirclean:
	rm -rf $(NBD_DIR)
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_NBD),y)
TARGETS+=nbd
endif
