class CopyistException(Exception):
    pass


class ConfigurationException(CopyistException):
    pass


class SyncException(CopyistException):
    pass
