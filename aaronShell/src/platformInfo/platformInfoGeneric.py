from abc import ABC, abstractmethod
from aaronShell.src.commandAST.command import Command
from aaronShell.src.commandlineInterface.commandlineInterface import ActiveCommandlineInterface
from platformInfoUbuntu import PlatforminfoUbuntu

class PlatformUnknown(Exception):
        """the platform is not known and no assumtions can be made"""
        def __init__(self, msg='The platform used is incompatible, make an issue specifying what you want to run on so it can be fully supported', *args, **kwargs): # type: ignore -> types dont matter for the exeptions
            super().__init__(msg, *args, **kwargs) # type: ignore -> types dont matter for the exeptions



class PlatformInfo(ABC):
    def __init__(self,commandlineInterface:ActiveCommandlineInterface):
        self._platform_name       :None|str = None
        self._nb_cpus             :None|int = None
        self._nb_cache_partitions :None|int = None

        self.commandline = commandlineInterface

    @classmethod
    def generate(cls,commandlineInterface:ActiveCommandlineInterface) -> 'PlatformInfo':
        #check if we are in windows
        if commandlineInterface.run_command_struct(Command("systeminfo")).is_sucsess():
            #probably in a windows system
            if commandlineInterface.run_command_struct(Command("ver")).is_sucsess():
                #probably in bash terminal
                raise PlatformUnknown()
            else:
                #probably in powershell terminal
                raise PlatformUnknown()
        else:
            versionResult = commandlineInterface.run_command_struct(Command("cat /proc/version"))
            if versionResult.is_sucsess():
                return PlatforminfoUbuntu(commandlineInterface)
            else:
                #we have no clue what we are working with
                raise PlatformUnknown()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        pass

    @property
    def platform_name(self) -> str:
        if self._platform_name == None:
            self._platform_name = self.get_platform_name()
        return self._platform_name
    
    @abstractmethod
    def get_nb_cpus(self) -> int:
        pass

    @property
    def nb_cpus(self) -> int:
        if self._nb_cpus == None:
            self._nb_cpus = self.get_nb_cpus()
        return self._nb_cpus
    
    @abstractmethod
    def get_nb_cache_partitions(self) -> int:
        pass

    @property
    def nb_cache_partitions(self) -> int:
        if self._nb_cache_partitions == None:
            self._nb_cache_partitions = self.get_nb_cache_partitions()
        return self._nb_cache_partitions
    

            
