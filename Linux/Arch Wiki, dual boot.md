## 1. Important information
### 1.1 Windows UEFI vs BIOS limitations
 **Windows 8/8.1** and **10** **x86_64** versions support booting in x86_64 UEFI mode from GPT disk only, OR in BIOS mode from MBR disk only. They do not support IA32 UEFI boot, x86_64 UEFI boot from MBR disk, or BIOS boot from GPT disk.
	**UEFI** - Unified Extensible Firmware
	**GUID Partition Table** (GPT) was introduced as part of the Unified Extensible Firmware Interface (UEFI) initiative. GPT provides a more flexible mechanism for partitioning disks than the older Master Boot Record (MBR) partitioning scheme that was common to PCs
	**GRUB** - GNU GRand Unified Bootloader
	
In general, Windows forces type of partitioning depending on the firmware mode used, i.e. if Windows is booted in UEFI mode, it can be installed only to a GPT disk. If Windows is booted in Legacy BIOS mode, it can be installed only to an MBR disk.

### 1.2. Bootloader UEFI vs BIOS limitations
**Chainloading** is when a boot loader loads another boot loader to begin the boot process.
**Note:** To dual-boot with Windows on same disk, Arch should follow the same firmware boot mode and partitioning combination used by the Windows installation.

### 1.3 UEFI Secure Boot
Advised to disable secure boot.  The only issue with regards to disabling UEFI Secure Boot support is that it requires physical access to the system to disable secure boot option in the firmware setup.

### 1.4 Fast startup and hibernation

## 2. Windows before Linux
### 2.1.2 UEFI systems
#### UEFI systems

If you already have Windows installed, it will already have created some partitions on a [GPT](https://wiki.archlinux.org/title/GPT "GPT")-formatted disk:

- a [Windows Recovery Environment](https://en.wikipedia.org/wiki/Windows_Recovery_Environment "wikipedia:Windows Recovery Environment") partition, generally of size 499 MiB, containing the files required to boot Windows (i.e. the equivalent of Linux's `/boot`),
- an [EFI system partition](https://wiki.archlinux.org/title/EFI_system_partition "EFI system partition") with a [FAT32](https://wiki.archlinux.org/title/FAT32 "FAT32") filesystem,
- a [Microsoft Reserved Partition](https://en.wikipedia.org/wiki/Microsoft_Reserved_Partition "wikipedia:Microsoft Reserved Partition"), generally of size 128 MiB,
- a Microsoft basic data partition with a NTFS filesystem, which corresponds to `C:`,
- potentially system recovery and backup partitions and/or secondary data partitions (corresponding often to `D:` and above).

Using the Disk Management utility in Windows, check how the partitions are labelled and which type gets reported. This will help you understand which partitions are essential to Windows, and which others you might repurpose. The Windows Disk Management utility can also be used to shrink Windows (NTFS) partitions to free up disk space for additional partitions for Linux.
You can then proceed with [partitioning](https://wiki.archlinux.org/title/Partitioning "Partitioning"), depending on your needs. The boot loader needs to support chainloading other EFI applications to dual boot Windows and Linux. An additional EFI system partition should not be created, as it may [prevent Windows from booting](https://support.microsoft.com/en-us/help/2879602/unable-to-boot-if-more-than-one-efi-system-partition-is-present).