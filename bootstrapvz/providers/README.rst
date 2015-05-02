Providers in bootstrap-vz represent various cloud providers and virtual machines.

bootstrap-vz is an extensible platform with loose coupling and a significant
amount of tooling, which allows for painless implementation of new providers.

The virtualbox provider for example is implemented in only 89 lines of python,
since most of the building blocks are a part of the common task library.
Only the kernel and guest additions installation are specific to that provider.
