VirtualBox
----------

The `VirtualBox <https://www.virtualbox.org/>`__ provider can bootstrap
to both .vdi and .vmdk images (raw images are also supported but do not
run in VirtualBox). It's advisable to always use vmdk images for
interoperability (e.g.
`OVF <http://en.wikipedia.org/wiki/Open_Virtualization_Format>`__ files
*should* support vdi files, but since they have no identifier URL not
even VirtualBox itself can import them). VirtualBox Guest Additions can
be installed automatically if the ISO is `provided in the
manifest <../../../manifests/#bootstrapper>`__.
