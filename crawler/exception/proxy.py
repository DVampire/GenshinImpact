class IpGetError(Exception):
    def __init__(self, message: str = 'IP get error'):
        self.message = message
        super().__init__(self.message)
