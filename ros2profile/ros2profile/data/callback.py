from typing import List

def _prettify(
    original: str,
) -> str:
    """
    Process symbol to make it more readable.

    * remove std::allocator
    * remove std::default_delete
    * bind object: remove placeholder

    :param original: the original symbol
    :return: the prettified symbol
    """
    pretty = original
    # remove spaces
    pretty = pretty.replace(' ', '')
    # allocator
    std_allocator = '_<std::allocator<void>>'
    pretty = pretty.replace(std_allocator, '')
    # default_delete
    std_defaultdelete = 'std::default_delete'
    if std_defaultdelete in pretty:
        dd_start = pretty.find(std_defaultdelete)
        template_param_open = dd_start + len(std_defaultdelete)
        # find index of matching/closing GT sign
        template_param_close = template_param_open
        level = 0
        done = False
        while not done:
            template_param_close += 1
            if pretty[template_param_close] == '<':
                level += 1
            elif pretty[template_param_close] == '>':
                if level == 0:
                    done = True
                else:
                    level -= 1
        pretty = pretty[:dd_start] + pretty[(template_param_close + 1):]
    # bind
    std_bind = 'std::_Bind<'
    if pretty.startswith(std_bind):
        # remove bind<>
        pretty = pretty.replace(std_bind, '')
        pretty = pretty[:-1]
        # remove placeholder stuff
        placeholder_from = pretty.find('*')
        placeholder_to = pretty.find(')', placeholder_from)
        pretty = pretty[:placeholder_from] + '?' + pretty[(placeholder_to + 1):]
    # remove dangling comma
    pretty = pretty.replace(',>', '>')
    # restore meaningful spaces
    if pretty.startswith('void'):
        pretty = 'void' + ' ' + pretty[len('void'):]
    if pretty.endswith('const'):
        pretty = pretty[:(len(pretty) - len('const'))] + ' ' + 'const'
    return pretty


class Callback:
    def __init__(self, callback_handle, symbol):
        self._handle = callback_handle
        self._symbol = symbol
        self._rclcpp_init_time = None

        self._events: List[CallbackEvent] = []


    def handle(self) -> int:
        return self._handle

    def symbol(self) -> str:
        return _prettify(self._symbol)

    def num_calls(self) -> int:
        return len(self._events)

    def events(self):
        return self._events

    def __repr__(self) -> str:
        return f'<Callback handle={self._handle}>'


class CallbackEvent:
    def __init__(self, callback_handle, is_intra_process):
        self._callback_handle = callback_handle
        self._is_intra_process = is_intra_process

        self._callback_start: int = -1
        self._callback_end:int = -1

        self._vpid = None
        self._vtid = None
        self._cpu_id = None

        self._trigger = None

    def trigger(self):
        return self._trigger

    def handle(self) -> int:
        return self._callback_handle

    def start(self) -> int:
        return self._callback_start

    def end(self) -> int:
        return self._callback_end

    def duration(self) -> int:
        return self.end() - self.start()

    def __repr__(self) -> str:
        return f'<CallbackEvent handle={self._callback_handle} start={self.start()} duration={self.duration()}>'
