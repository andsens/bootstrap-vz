from base import Phase

preparation = Phase('Initializing connections, fetching data etc.')
volume_creation = Phase('Creating the volume to bootstrap onto')
volume_preparation = Phase('Formatting the bootstrap volume')
volume_mounting = Phase('Mounting bootstrap volume')
os_installation = Phase('Installing the operating system')
system_modification = Phase('Installing software, modifying configuration files etc.')
system_cleaning = Phase('Removing sensitive data, temporary files and other leftovers')
volume_unmounting = Phase('Unmounting the bootstrap volume')
image_registration = Phase('Uploading/Registering with the provider')
cleaning = Phase('Removing temporary files')

order = [preparation,
         volume_creation,
         volume_preparation,
         volume_mounting,
         os_installation,
         system_modification,
         system_cleaning,
         volume_unmounting,
         image_registration,
         cleaning,
         ]
