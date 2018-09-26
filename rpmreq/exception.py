class RPMReqException(Exception):
    msg_fmt = "An unknown error occurred"

    def __init__(self, msg=None, **kwargs):
        self.kwargs = kwargs
        if not msg:
            try:
                msg = self.msg_fmt % kwargs
            except Exception:
                msg = self.msg_fmt
        super(RPMReqException, self).__init__(msg)


class NotADirectory(RPMReqException):
    msg_fmt = "Not a directory: %(path)s"


class RemoteFileFetchFailed(RPMReqException):
    msg_fmt = "Failed to fetch remote file with status %(code)s: %(url)s"


class RepoMDParsingFailed(RPMReqException):
    msg_fmt = "Failed to parse repository metadata :-/"


class InvalidUsage(RPMReqException):
    msg_fmt = "Invalid usage: %(why)s"
