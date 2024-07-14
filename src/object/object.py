import enum
import hashlib
from typing import Callable

from src.ast.ast import BlockStatement, Identifier
from src.object.environment import Environment

# Define BuiltinFunction as a callable that takes any number of arguments and returns an Object
BuiltinFunction = Callable[..., "Object"]


class ObjectType(enum.Enum):
    NULL = "NULL"
    ERROR = "ERROR"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    RETURN_VALUE = "RETURN_VALUE"
    FUNCTION = "FUNCTION"
    BUILTIN = "BUILTIN"
    ARRAY = "ARRAY"
    HASH = "HASH"


class HashKey:
    def __init__(self, obj_type: str, value: int):
        self.type = obj_type
        self.value = value

    def __key(self):
        return (self.type, self.value)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        assert isinstance(other, HashKey)
        return hash(self.type) == hash(other.type) and hash(self.value) == hash(other.value)


class Hashable:
    def hash_key(self) -> HashKey:
        raise NotImplementedError


class Object:
    def type(self) -> ObjectType:
        raise NotImplementedError

    def inspect(self) -> str:
        raise NotImplementedError


class Integer(Object, Hashable):
    def __init__(self, value: int):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.INTEGER

    def inspect(self) -> str:
        return str(self.value)

    def hash_key(self) -> HashKey:
        return HashKey(self.type().value, self.value)


class Boolean(Object, Hashable):
    def __init__(self, value: bool):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.BOOLEAN

    def inspect(self) -> str:
        return str(self.value).lower()

    def hash_key(self) -> HashKey:
        value = 1 if self.value else 0
        return HashKey(self.type().value, value)


class Null(Object):
    def type(self) -> ObjectType:
        return ObjectType.NULL

    def inspect(self) -> str:
        return "null"


class ReturnValue(Object):
    def __init__(self, value: Object):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.RETURN_VALUE

    def inspect(self) -> str:
        return self.value.inspect()


class Error(Object):
    def __init__(self, message: str):
        self.message = message

    def type(self) -> ObjectType:
        return ObjectType.ERROR

    def inspect(self) -> str:
        return f"ERROR: {self.message}"


class Function(Object):
    def __init__(self, parameters: list[Identifier], body: BlockStatement, env: Environment):
        self.parameters = parameters
        self.body = body
        self.env = env

    def type(self) -> ObjectType:
        return ObjectType.FUNCTION

    def inspect(self) -> str:
        params = [str(p) for p in self.parameters]
        params_str = ", ".join(params)
        body_str = str(self.body)
        return f"fn({params_str}) {{\n{body_str}\n}}"


class String(Object, Hashable):
    def __init__(self, value: str):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.STRING

    def inspect(self) -> str:
        return self.value

    def hash_key(self) -> HashKey:
        h = hashlib.sha256()
        h.update(self.value.encode("utf-8"))
        return HashKey(self.type().value, int(h.hexdigest(), 16))


class BuiltIn(Object):
    def __init__(self, fn: BuiltinFunction):
        self.fn = fn

    def type(self) -> ObjectType:
        return ObjectType.BUILTIN

    def inspect(self) -> str:
        return "builtin function"


class Array(Object):
    def __init__(self, elements: list[Object]):
        self.elements = elements

    def type(self) -> ObjectType:
        return ObjectType.ARRAY

    def inspect(self) -> str:
        elements_str = ", ".join([e.inspect() for e in self.elements])
        return f"[{elements_str}]"


class HashPair:
    def __init__(self, key: Object, value: Object):
        self.key = key
        self.value = value


class Hash(Object):
    def __init__(self, pairs: dict[HashKey, HashPair]):
        self.pairs = pairs

    def type(self) -> ObjectType:
        return ObjectType.HASH

    def inspect(self) -> str:
        pairs_str = ", ".join([f"{pair.key.inspect()}: {pair.value.inspect()}" for pair in self.pairs.values()])
        return f"{{{pairs_str}}}"
