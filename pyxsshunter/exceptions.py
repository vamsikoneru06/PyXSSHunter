class PyXSSHunterError(Exception):
    pass

class InvalidURLException(PyXSSHunterError):
    pass

class ScanError(PyXSSHunterError):
    pass