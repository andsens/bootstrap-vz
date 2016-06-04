from bootstrapvz.base.fs.volume import Volume


class Folder(Volume):

    # Override the states this volume can be in (i.e. we can't "format" or "attach" it)
    events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'attached'},
              {'name': 'delete', 'src': 'attached', 'dst': 'deleted'},
              ]

    extension = 'chroot'

    def create(self, path):
        self.fsm.create(path=path)

    def _before_create(self, e):
        import os
        self.path = e.path
        os.mkdir(self.path)

    def _before_delete(self, e):
        from shutil import rmtree
        rmtree(self.path)
        del self.path
