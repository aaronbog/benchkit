from command import Command
from abc import ABC, abstractmethod
import paramiko

"""
This restriction is placed such that we are sure that we clean up our connections and running processes
"""
class CommandlineInterfaceNotInContext(Exception):
        """Error raised when CommandlineInterface is used outside of with statements"""
        def __init__(self, msg='CommandlineInterface can only be used iside of a with statement', *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

class CommandlineInterface(ABC):

    def __enter__(self) -> 'CommandlineInterface':
        ret = self._enter()
        self.is_inside_with = True
        return ret

    @abstractmethod
    def _enter(self) -> 'CommandlineInterface':
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        self.is_inside_with = False
        return self._exit(exc_type, exc_value, traceback)

    @abstractmethod
    def _exit(self, exc_type, exc_value, traceback):
        pass
        

    @abstractmethod
    def run_command(self,command:Command) -> None:
        pass
    
    @classmethod
    def remoteInterface(cls,hostname,port,username):
        return RemoteInterface(hostname,port,username)

    @classmethod
    def localInterface(cls):
        LocalInterface()

    def _assertIsInsideWithStatement(self):
        if not self.is_inside_with:
            raise CommandlineInterfaceNotInContext()

class RemoteInterface(CommandlineInterface):
    def __init__(self,hostname,port,username):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.hostname = hostname
        self.port = port
        self.username = username

    def __enter__(self) -> 'CommandlineInterface':
        return super().__enter__()

    def _enter(self) -> 'CommandlineInterface':
        self.client.connect(hostname=self.hostname,port=self.port,username=self.username)
        return self

    def _exit(self, exc_type, exc_value, traceback):
        self.client.close()


    def run_command(self,command:Command) -> None:
        assert(isinstance(command, Command))

        self._assertIsInsideWithStatement()
        stdin, stdout, stderr = self.client.exec_command(command.get_command())
        exit_status = stdout.channel.recv_exit_status()
        out=stdout.read()
        print(out)
        print(exit_status)

class LocalInterface(CommandlineInterface):
    def __init__(self):
        pass

    def _enter(self):
        pass

    def _exit(self, exc_type, exc_value, traceback):
        pass


    def run_command(self,command:float):
        pass
    