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
