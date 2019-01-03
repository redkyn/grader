import docker
import logging

logger = logging.getLogger(__name__)


class DockerClientMixin(object):
    """A mixin class that gives subclasses access to a docker Client
    object.
    """

    @property
    def docker_cli(self):
        """A docker Client object. Always returns the same one."""
        if not hasattr(self, "_docker_cli"):
            logger.debug("Creating Docker client")
            self._docker_cli = docker.APIClient(
                base_url="unix://var/run/docker.sock",
                version="auto"
            )
        return self._docker_cli
