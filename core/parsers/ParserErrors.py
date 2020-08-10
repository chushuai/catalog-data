class PandaDSError(Exception):
    def __init__(self, *args):
        self.message = "Unknown PandaDS error."
        if args:
            self.message = args[0]
        super().__init__(self.message)

    def __str__(self):
        return 'PandaDSError, {0} '.format(self.message)


class BaseParsingError(PandaDSError):
    pass


class ParsingError(PandaDSError):
    pass


class ParsingSplitError(PandaDSError):
    pass


class SplitError(PandaDSError):
    pass
