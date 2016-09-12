from bootstrapvz.base.phase import Phase

validation = Phase('Validation', 'Validating data, files, etc.')
preparation = Phase('Preparation', 'Initializing connections, fetching data etc.')
volume_creation = Phase('Volume creation', 'Creating the volume to bootstrap onto')
volume_preparation = Phase('Volume preparation', 'Formatting the bootstrap volume')
volume_mounting = Phase('Volume mounting', 'Mounting bootstrap volume')
os_installation = Phase('OS installation', 'Installing the operating system')
package_installation = Phase('Package installation', 'Installing software')
system_modification = Phase('System modification', 'Modifying configuration files, adding resources, etc.')
user_modification = Phase('User modification', 'Running user specified modifications')
system_cleaning = Phase('System cleaning', 'Removing sensitive data, temporary files and other leftovers')
volume_unmounting = Phase('Volume unmounting', 'Unmounting the bootstrap volume')
image_registration = Phase('Image registration', 'Uploading/Registering with the provider')
cleaning = Phase('Cleaning', 'Removing temporary files')

order = [validation,
         preparation,
         volume_creation,
         volume_preparation,
         volume_mounting,
         os_installation,
         package_installation,
         system_modification,
         user_modification,
         system_cleaning,
         volume_unmounting,
         image_registration,
         cleaning,
         ]
