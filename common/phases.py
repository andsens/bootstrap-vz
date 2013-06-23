from base import Phase

preparation = Phase('Initializing connections, fetching data etc.')
volume_creation = Phase('Creating the volume to bootstrap onto')
volume_preparation = Phase('Formatting the bootstrap volume')
volume_mounting = Phase('Mounting bootstrap volume')
install_os = Phase('Installing the operating system')
modify_system = Phase('Installing software, modifying configuration files etc.')
clean_system = Phase('Removing sensitive data, temporary files and other leftovers')
unmount_volume = Phase('Unmounting the bootstrap volume')
register_image = Phase('Uploading/Registering with the provider')
cleanup = Phase('Removing temporary files')

order = [preparation
        ,volume_creation
        ,volume_preparation
        ,volume_mounting
        ,install_os
        ,modify_system
        ,clean_system
        ,unmount_volume
        ,register_image
        ,cleanup
        ]
