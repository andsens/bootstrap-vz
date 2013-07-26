from base import Task
from common import phases
from common.exceptions import TaskError
from common.tools import log_check_call
from bootstrap import Bootstrap
import os

class FormatVolume(Task):
	description = 'Formatting the volume'
	phase = phases.volume_preparation

	def run(self, info):
                mkmount = ['/usr/bin/qemu-img', 'create', '-f', 'raw', info.manifest.bootstrapper['image_file'], str(info.manifest.volume['size'])+'M']
                log_check_call(mkmount)

		# parted
		log_check_call(['parted','-a', 'optimal', '-s', info.manifest.bootstrapper['image_file'], "mklabel", "msdos"])
                log_check_call(['parted', '-a', 'optimal', '-s', info.manifest.bootstrapper['image_file'], "--", "mkpart", "primary", "ext4", "1", "-1"])
		log_check_call(['parted','-a', 'optimal', '-s', info.manifest.bootstrapper['image_file'], "--", "set", "1", "boot", "on"])
		log_check_call(['kpartx','-a','-v', info.manifest.bootstrapper['image_file']])


		#loopcmd = ['/sbin/losetup', '/dev/loop0', info.manifest.bootstrapper['image_file']]
		#log_check_call(loopcmd)
                mkfs = [ '/sbin/mkfs.{fs}'.format(fs=info.manifest.volume['filesystem']), '-m', '1', '-v', '/dev/mapper/loop0p1']
                log_check_call(mkfs)




class TuneVolumeFS(Task):
	description = 'Tuning the bootstrap volume filesystem'
	phase = phases.volume_preparation
	after = [FormatVolume]

	def run(self, info):
		#dev_path = info.bootstrap_device['path']
                #dev_path = info.manifest.bootstrapper['image_file']
		dev_path = '/dev/mapper/loop0p1'
		# Disable the time based filesystem check
		log_check_call(['/sbin/tune2fs', '-i', '0', dev_path])


class AddXFSProgs(Task):
	description = 'Adding `xfsprogs\' to the image packages'
	phase = phases.preparation

	def run(self, info):
		include, exclude = info.img_packages
		include.add('xfsprogs')


class CreateMountDir(Task):
	description = 'Creating mountpoint for the bootstrap volume'
	phase = phases.volume_mounting

	def run(self, info):
		import os
		mount_dir = info.manifest.bootstrapper['mount_dir']
		info.root = mount_dir
		# Works recursively, fails if last part exists, which is exaclty what we want.
		os.makedirs(mount_dir)


class MountVolume(Task):
	description = 'Mounting the bootstrap volume'
	phase = phases.volume_mounting
	after = [CreateMountDir]

	def run(self, info):
		with open('/proc/mounts') as mounts:
			for mount in mounts:
				if info.root in mount:
					msg = 'Something is already mounted at {root}'.format(root=info.root)
					raise TaskError(msg)

		log_check_call(['/bin/mount', '-t', info.manifest.volume['filesystem'], '/dev/mapper/loop0p1', info.root])

class MountSpecials(Task):
	description = 'Mounting special block devices'
	phase = phases.os_installation
	after = [Bootstrap]

	def run(self, info):
		log_check_call(['/bin/mount', '--bind', '/dev', '{root}/dev'.format(root=info.root)])
		log_check_call(['/usr/sbin/chroot', info.root, '/bin/mount', '-t', 'proc', 'none', '/proc'])
		log_check_call(['/usr/sbin/chroot', info.root, '/bin/mount', '-t', 'sysfs', 'none', '/sys'])
		log_check_call(['/usr/sbin/chroot', info.root, '/bin/mount', '-t', 'devpts', 'none', '/dev/pts'])


class UnmountSpecials(Task):
	description = 'Unmunting special block devices'
	phase = phases.volume_unmounting

	def run(self, info):
		log_check_call(['/usr/sbin/chroot', info.root, '/bin/umount', '/dev/pts'])
		log_check_call(['/usr/sbin/chroot', info.root, '/bin/umount', '/sys'])
		log_check_call(['/usr/sbin/chroot', info.root, '/bin/umount', '/proc'])
		log_check_call(['/bin/umount', '{root}/dev'.format(root=info.root)])


class UnmountVolume(Task):
	description = 'Unmounting the bootstrap volume'
	phase = phases.volume_unmounting
	after = [UnmountSpecials]

	def run(self, info):
		log_check_call(['/bin/umount', info.root])
                #log_check_call(['/sbin/losetup', '-d', '/dev/loop0'])
		log_check_call(['kpartx','-d', info.manifest.bootstrapper['image_file']])



class DeleteMountDir(Task):
	description = 'Deleting mountpoint for the bootstrap volume'
	phase = phases.volume_unmounting
	after = [UnmountVolume]

	def run(self, info):
		import os
		os.rmdir(info.root)
		del info.root


class ModifyFstab(Task):
	description = 'Adding root volume to the fstab'
	phase = phases.system_modification

	def run(self, info):
		import os.path
		mount_opts = ['defaults']
		if info.manifest.volume['filesystem'].lower() in ['ext2', 'ext3', 'ext4']:
			mount_opts.append('barrier=0')
		if info.manifest.volume['filesystem'].lower() == 'xfs':
			mount_opts.append('nobarrier')
		fstab_path = os.path.join(info.root, 'etc/fstab')
		with open(fstab_path, 'a') as fstab:
			fstab.write(('/dev/sda1 /     {filesystem}    {mount_opts} 1 1\n'
			             .format(filesystem=info.manifest.volume['filesystem'].lower(),
			                     mount_opts=','.join(mount_opts))))
                log_check_call(['/usr/sbin/chroot', info.root, 'cat', '/etc/fstab'])

class InstallMbr(Task):
	description = 'Install MBR'
	phase = phases.system_modification

	def run(self, info):
		log_check_call(['install-mbr', info.manifest.bootstrapper['image_file']])
