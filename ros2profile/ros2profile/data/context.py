class Context:
    '''
    Context represents a single rcl_init invokation.
    Typically, there is one context associate with each process in the graph.
    '''
    def __init__(self, context_handle: int, version: str):
        self._handle = context_handle
        self._version = version

    def __repr__(self) -> str:
        return f'<Context handle={self._handle} version={self._version}>'

    @property
    def handle(self) -> int:
        '''
        The identifier of this context
        '''
        return self._handle

    @handle.setter
    def handle(self, value: int) -> None:
        self._handle = value

    @property
    def version(self) -> str:
        '''
        The version of this context
        '''
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value
