from base import Phase


class Preparation(Phase):
	description = 'Initializing connections, fetching data etc.'

class VolumeCreation(Phase):
	description = 'Creating the volume to bootstrap onto'

class VolumePreparation(Phase):
	description = 'Formatting the bootstrap volume'

class VolumeMounting(Phase):
	description = 'Mounting bootstrap volume'

class InstallOS(Phase):
	description = 'Installing the operating system'

class ModifySystem(Phase):
	description = 'Installing software, modifying configuration files etc.'

class CleanSystem(Phase):
	description = 'Removing sensitive data, temporary files and other leftovers'

class UnmountVolume(Phase):
	description = 'Unmounting the bootstrap volume'

class RegisterImage(Phase):
	description = 'Uploading/Registering with the provider'

class Cleanup(Phase):
	description = 'Removing temporary files'

order = [Preparation,
         VolumeCreation,
         VolumePreparation,
         VolumeMounting,
         InstallOS,
         ModifySystem,
         CleanSystem,
         UnmountVolume,
         RegisterImage,
         Cleanup
        ]
