from platformInfoGeneric import PlatformInfo


class PlatforminfoUbuntu(PlatformInfo):
    def get_platform_name(self) -> str:
        return "aaa"

    def get_nb_cpus(self) -> int:
        return 24
    
    def get_nb_cache_partitions(self) -> int:
        return 24