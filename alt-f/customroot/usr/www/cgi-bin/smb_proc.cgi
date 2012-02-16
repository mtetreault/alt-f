#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_FSTAB=/etc/fstab
CONF_SMB=/etc/samba/smb.conf

if test "$submit" = "Advanced"; then
	# embed_page "http://$(hostname -i | sed 's/ //'):901"
	if echo $HTTP_REFERER | grep -q '^https://'; then
		embed_page "https://$HTTP_HOST:902"
    else
		embed_page "http://$HTTP_HOST:901"
	fi

elif test -n "$unMount"; then
	mp=$(httpd -d "$unMount")
	res="$(umount $mp 2>&1)"
	st=$?
	if test $st != 0; then
		msg "Error $st: $res"
	fi

elif test -n "$Mount"; then
	mp=$(httpd -d "$Mount")
	res="$(mount $mp 2>&1)"
	st=$?
	# /etc/mtab is a link to /proc/mounts, mount.cifs cant lock it
	if test $st != 0 -a $st != 16; then 
		msg "Error $st: $res"
	fi

elif test "$submit" = "Submit"; then

	sed -i '/\(\t\| \)cifs\(\t\| \)/d' $CONF_FSTAB

	for i in $(seq 1 $import_cnt); do
		if test -z "$(eval echo \$rhost_$i)" -o -z "$(eval echo \$rdir_$i)" -o \
			-z "$(eval echo \$mdir_$i)" -o -z "$(eval echo \$mopts_$i)"; then continue; fi

		rdir=$(path_escape "$(httpd -d $(eval echo \$rdir_$i))")
		mdir=$(path_escape "$(httpd -d $(eval echo \$mdir_$i))")

		httpd -d "$(eval echo \$fstab_en_${i}//\$rhost_${i}/\"$rdir $mdir\" cifs \$mopts_$i 0 0)"
		echo
	done  >> $CONF_FSTAB

	cp $CONF_SMB $CONF_SMB-
	awk '
		{ pshare($0) }

		function pshare(line) {
			s = index(line, "[") ; e = index(line, "]")
			share_name = tolower(substr(line, s+1, e-s-1))
			if (share_name == "global" || share_name == "printers") {
				print $0
				while (st = getline) {
					if (substr($0,1,1) == "[")
						break
					printf "%s\n", $0
				}
				if (st == 0)
					exit
			} else
				if (! getline)
					exit
			pshare($0)
		}
	' $CONF_SMB- > $CONF_SMB

	for i in $(seq 1 $smb_cnt); do
		if test -z "$(eval echo \$ldir_$i)" -o -z "$(eval echo \$shname_$i)"; then continue; fi

		t=$(httpd -d "$(eval echo \$shname_$i)"); echo -e "[$t]"
		t=$(httpd -d "$(eval echo comment = \$cmt_$i)"); echo -e "\t$t"
		t=$(httpd -d "$(eval echo path = \$ldir_$i)"); echo -e "\t$t"

		t=$(httpd -d "$(eval echo \$user_$i)")
		if test "$t" = "anybody"; then
			echo -e "\tpublic = yes"
		elif test "$t" = "nonpublic"; then
			echo -e "\tpublic = no"
		else
			echo -e "\tvalid users = $t"
		fi

		avail=no
		if test -z "$(eval echo \$avail_$i)"; then
			avail=yes
		fi
		echo -e "\tavailable = $avail"

		if test -z "$(eval echo \$browse_$i)"; then
			echo -e "\tbrowseable = no"
		fi

		ro=yes
		if test -z "$(eval echo \$rdonly_$i)"; then
			ro=no
		fi
		echo -e "\tread only = $ro"

		if test -n "$(eval echo \$inhperms_$i)"; then
			echo -e "\tinherit permissions = yes"
		fi

		echo

	done  >> $CONF_SMB

	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi	

fi

#enddebug
gotopage /cgi-bin/smb.cgi
