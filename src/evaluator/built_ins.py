from src.object.object import Array, BuiltIn, Error, Integer, Null, Object, ObjectType, String


def new_error(format_string, *args) -> Error:
    return Error(format_string % args)


def builtin_len(*args: Object) -> Error | Integer:
    if len(args) != 1:
        return new_error("wrong number of arguments. got=%d, want=1", len(args))

    arg: Object = args[0]
    if isinstance(arg, Array):
        return Integer(len(arg.elements))
    elif isinstance(arg, String):
        return Integer(len(arg.value))
    else:
        return new_error("argument to `len` not supported, got %s", arg.type().value)


def builtin_puts(*args: Object) -> Null:
    for arg in args:
        print(arg.inspect())

    return Null()


def builtin_first(*args: Object) -> Error | Object | Null:
    if len(args) != 1:
        return new_error("wrong number of arguments. got=%d, want=1", len(args))

    arg: Object = args[0]
    if arg.type() != ObjectType.ARRAY:
        return new_error("argument to `first` must be ARRAY, got %s", arg.type().value)

    arr: Object = arg
    assert isinstance(arr, Array)
    if len(arr.elements) > 0:
        return arr.elements[0]

    return Null()


def builtin_last(*args: Object) -> Error | Object | Null:
    if len(args) != 1:
        return new_error("wrong number of arguments. got=%d, want=1", len(args))

    arg: Object = args[0]
    if arg.type() != ObjectType.ARRAY:
        return new_error("argument to `last` must be ARRAY, got %s", arg.type().value)

    arr: Object = arg
    assert isinstance(arr, Array)
    length = len(arr.elements)
    if length > 0:
        return arr.elements[length - 1]

    return Null()


def builtin_rest(*args: Object) -> Error | Array | Null:
    if len(args) != 1:
        return new_error("wrong number of arguments. got=%d, want=1", len(args))

    arg: Object = args[0]
    if arg.type() != ObjectType.ARRAY:
        return new_error("argument to `rest` must be ARRAY, got %s", arg.type().value)

    arr: Object = arg
    assert isinstance(arr, Array)
    length = len(arr.elements)
    if length > 0:
        new_elements: list[Object] = arr.elements[1:]
        return Array(new_elements)

    return Null()


def builtin_push(*args: Object) -> Error | Array:
    if len(args) != 2:
        return new_error("wrong number of arguments. got=%d, want=2", len(args))

    arg: Object = args[0]
    if arg.type() != ObjectType.ARRAY:
        return new_error("argument to `push` must be ARRAY, got %s", arg.type().value)

    arr: Object = arg
    assert isinstance(arr, Array)
    new_elements: list[Object] = arr.elements + [args[1]]
    return Array(new_elements)


builtin_funcs: dict[str, BuiltIn] = {
    "len": BuiltIn(builtin_len),
    "puts": BuiltIn(builtin_puts),
    "first": BuiltIn(builtin_first),
    "last": BuiltIn(builtin_last),
    "rest": BuiltIn(builtin_rest),
    "push": BuiltIn(builtin_push),
}
