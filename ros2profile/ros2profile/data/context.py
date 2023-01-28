class Context:
    def __init__(self, context_handle: int, version: str):
        self._handle = context_handle
        self._version = version

    def __repr__(self) -> str:
        return f'<Context handle={self._handle} version={self._version}>'
