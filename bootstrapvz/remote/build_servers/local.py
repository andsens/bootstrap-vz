from build_server import BuildServer


class LocalBuildServer(BuildServer):

	def run(self, manifest):
		from bootstrapvz.base.main import run
		return run(manifest)
