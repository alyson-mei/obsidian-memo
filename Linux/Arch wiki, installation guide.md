## 1 Pre-installation
### 1.1 Acquire an installation image
Torrent
### 1.2 Verify signature
### 1.3 Prepare an installation medium\
USB with Ventoy
### 1.4 Boot the live environment


### 1.5 Set the console keyboard layout and font
[Console fonts](https://wiki.archlinux.org/title/Console_fonts "Console fonts") are located in `/usr/share/kbd/consolefonts/` and can likewise be set with [setfont(8)](https://man.archlinux.org/man/setfont.8) omitting the path and file extension. For example, to use one of the largest fonts suitable for [HiDPI screens](https://wiki.archlinux.org/title/HiDPI#Linux_console_(tty) "HiDPI"), 
\# setfont ter-132b // much better :)

### 1.6 Verify the boot mode
\# cat /sys/firmware/efi/fw_platform_size //64
If the command returns `64`, then system is booted in UEFI mode and has a 64-bit x64 UEFI. If the command returns `32`, then system is booted in UEFI mode and has a 32-bit IA32 UEFI; while this is supported, it will limit the boot loader choice to systemd-boot and GRUB.

### 1.7 Connect to the internet
\# ip link -> l0, enp0s31f6, wlan0
Connect to the network:
- Ethernet—plug in the cable.
- Wi-Fi—authenticate to the wireless network using [iwctl](https://wiki.archlinux.org/title/Iwctl "Iwctl").
- Mobile broadband modem—connect to the mobile network with the [mmcli](https://wiki.archlinux.org/title/Mmcli "Mmcli") utility.

		# iwctl
		[iwd]# device list // name = wlan0
		[iwd]# station _name_ scan (initiation) // no return
		$ iwctl --passphrase _passphrase_ station _name_ connect _SSID_ // no quotes, SSID is the name of the network
		# ping archlinux.org
### 1.8 Update the system clock
	\# timedatectl
### 1.9 Partition the disks
!!! you should unallocate before partitioning (not just make Ext4)
Before:  
- System reserved (OEM service volume) 100 MB
- System reserved 16 MB
- OEM System volume 521 MB
- Main windows 128.85 GB
- Unallocated 109 GB
	\# lsblk
### 1.10 Format the partitions
	\# mkfs.ext-4 /dev/nvme0n1p7 //58G, /home
	# mkfs.ext-4 /dev/nvme0n1p8 //42G, /root
	# mkfs.fat -F 32 /dev/nvme0n1p5 //1G, EFI
	# mkswap /dev/nvme0n1p6 //8G, swap
### 1.11 Mount the file systems
	# mount /dev/_root_partition_ /mnt
	# mount /dev/_home_partition_ /mnt/home
	# mount --mkdir /dev/_efi_system_partition_ /mnt/boot/efi?
	# swapon /dev/_swap_partition_
## 2. Installation
### 2.1 Select the mirrors
### 2.2 Install essential packages
	# pacstrap /mnt base linux linux-firmware sof-firmware base-devel grub efibootmgr nano networkmanager
## 3. Configure the system
### 3.1 Fstab
Generate an [fstab](https://wiki.archlinux.org/title/Fstab "Fstab") file (use `-U` or `-L` to define by [UUID](https://wiki.archlinux.org/title/UUID "UUID") or labels, respectively):

	# genfstab -U /mnt >> /mnt/etc/fstab
### 3.2 Chroot
[Change root](https://wiki.archlinux.org/title/Change_root "Change root") into the new system

	# arch-chroot /mnt
### 3.3 Time

Set the [time zone](https://wiki.archlinux.org/title/Time_zone "Time zone"):
	
	# ln -sf /usr/share/zoneinfo/_Region_/_City_ /etc/localtime
	# hwclock --systohc
### 3.4 Localization
edit `/etc/locale.gen`, uncomment `en_US.UTF-8 UTF-8.

	# locale-gen
Create /etc/locale.conf with LANG=en_US.UTF-8
Layout in /etc/vconsole.conf
### 3.5 Network configuration
/etc/hostname
_yourhostname_

### 3.6 Initramfs
-

### 3.7 Root password
	# passwd
### 3.8 Boot loader
	# grub-install --target=x86_64-efi --efi-directory=/boot/efi
	# grub-mkconfig -o /boot/grub/grub.cfg

### 3.9 Make user
	#useradd -d /home -G wheel -s /bin/bash alyson
	#passwd alyson
### 3.10 Add to sudoers
	# su alyson
	# sudo pacman -Syu 
Not in sudoers

	# EDITOR=nano visudo
### 3.11 Enabling core services 
	# systemctl enable NetworkManager

### 3.12 Finishing
	# umount -a
	# reboot

## 4 After installation
### 4.1 Install KDE Plasma
	# sudo pacman -S plasma sddm
### 4.2 Additional packages
	# sudo pacman -S konsole kate firefox