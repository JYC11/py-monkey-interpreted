from src.ast.ast import (
    ArrayLiteral,
    BlockStatement,
    BooleanLiteral,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    HashLiteral,
    Identifier,
    IfExpression,
    IndexExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    Node,
    PrefixExpression,
    Program,
    ReturnStatement,
    StringLiteral,
)
from src.evaluator.built_ins import builtin_funcs
from src.object.environment import Environment, new_enclosed_environment
from src.object.object import (
    Array,
    Boolean,
    BuiltIn,
    Error,
    Function,
    Hash,
    Hashable,
    HashKey,
    HashPair,
    Integer,
    Null,
    Object,
    ObjectType,
    ReturnValue,
    String,
)

TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()


def eval_program(program: Program, env: Environment):
    for statement in program.statements:
        result = evaluate(statement, env)
        if isinstance(result, ReturnValue):
            return result.value
        if isinstance(result, Error):
            return result
    return result


def eval_block_statement(block: BlockStatement, env: Environment):
    for statement in block.statements:
        result = evaluate(statement, env)
        if result:
            if result.type() == ObjectType.RETURN_VALUE or result.type() == ObjectType.ERROR:
                return result
    return result


def native_bool_to_boolean_object(value: bool) -> Boolean:
    return TRUE if value else FALSE


def eval_prefix_expression(operator: str, right: Object) -> Boolean | Error | Integer:
    if operator == "!":
        return eval_bang_operator_expression(right)
    elif operator == "-":
        return eval_minus_prefix_operator_expression(right)
    else:
        return new_error(f"unknown operator: {operator}{right.type().value}")


def eval_infix_expression(operator: str, left: Object, right: Object) -> Integer | Boolean | Error | String:
    if left.type() == ObjectType.INTEGER and right.type() == ObjectType.INTEGER:
        return eval_integer_infix_expression(operator, left, right)
    elif left.type() == ObjectType.STRING and right.type() == ObjectType.STRING:
        return eval_string_infix_expression(operator, left, right)
    elif operator == "==":
        return native_bool_to_boolean_object(left == right)
    elif operator == "!=":
        return native_bool_to_boolean_object(left != right)
    elif left.type() != right.type():
        return new_error(f"type mismatch: {left.type().value} {operator} {right.type().value}")
    else:
        return new_error(f"unknown operator: {left.type().value} {operator} {right.type().value}")


def eval_bang_operator_expression(right: Object) -> Boolean:
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE


def eval_minus_prefix_operator_expression(right: Object) -> Error | Integer:
    if right.type() != ObjectType.INTEGER:
        return new_error(f"unknown operator: -{right.type().value}")
    assert isinstance(right, Integer)
    value: int = right.value
    return Integer(-value)


def eval_integer_infix_expression(operator: str, left: Object, right: Object) -> Integer | Boolean | Error:
    assert isinstance(left, Integer)
    left_val: int = left.value
    assert isinstance(right, Integer)
    right_val: int = right.value
    if operator == "+":
        return Integer(left_val + right_val)
    elif operator == "-":
        return Integer(left_val - right_val)
    elif operator == "*":
        return Integer(left_val * right_val)
    elif operator == "/":
        return Integer(int(left_val / right_val))
    elif operator == "<":
        return native_bool_to_boolean_object(left_val < right_val)
    elif operator == ">":
        return native_bool_to_boolean_object(left_val > right_val)
    elif operator == "==":
        return native_bool_to_boolean_object(left_val == right_val)
    elif operator == "!=":
        return native_bool_to_boolean_object(left_val != right_val)
    else:
        return new_error(f"unknown operator: {left.type().value} {operator} {right.type().value}")


def eval_string_infix_expression(operator: str, left: Object, right: Object) -> Error | String:
    if operator != "+":
        return new_error(f"unknown operator: {left.type().value} {operator} {right.type().value}")
    assert isinstance(left, String)
    left_val: str = left.value
    assert isinstance(right, String)
    right_val: str = right.value
    return String(left_val + right_val)


def eval_if_expression(ie: IfExpression, env: Environment) -> Object | Null:
    condition: Object = evaluate(ie.condition, env)
    if is_error(condition):
        return condition
    if is_truthy(condition):
        return evaluate(ie.consequence, env)
    elif ie.alternative:
        return evaluate(ie.alternative, env)
    else:
        return NULL


def eval_identifier(node: Identifier, env: Environment):
    val, ok = env.get(node.value)
    if ok:
        return val
    if node.value in builtin_funcs:
        return builtin_funcs[node.value]
    return new_error(f"identifier not found: {node.value}")


def is_truthy(obj: Object) -> bool:
    if obj == NULL:
        return False
    elif obj == TRUE:
        return True
    elif obj == FALSE:
        return False
    else:
        return True


def new_error(message: str) -> Error:
    return Error(message)


def is_error(obj: Object | None) -> bool:
    return obj is not None and obj.type() == ObjectType.ERROR


def eval_expressions(exps: list[Expression], env: Environment) -> list[Object]:
    result: list[Object] = []
    for e in exps:
        evaluated: Object = evaluate(e, env)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def apply_function(fn: Object, args: list[Object]) -> Object | Error:
    if isinstance(fn, Function):
        extended_env: Environment = extend_function_env(fn, args)
        evaluated: Object = evaluate(fn.body, extended_env)
        return unwrap_return_value(evaluated)
    elif isinstance(fn, BuiltIn):
        return fn.fn(*args)
    else:
        return new_error(f"not a function: {fn.type().value}")


def extend_function_env(fn: Function, args: list[Object]) -> Environment:
    env: Environment = new_enclosed_environment(fn.env)
    for param_idx, param in enumerate(fn.parameters):
        env.set(param.value, args[param_idx])
    return env


def unwrap_return_value(obj: Object) -> Object:
    if isinstance(obj, ReturnValue):
        return obj.value
    return obj


def eval_index_expression(left: Object, index: Object) -> Null | Object | Error:
    if left.type() == ObjectType.ARRAY and index.type() == ObjectType.INTEGER:
        return eval_array_index_expression(left, index)
    elif left.type() == ObjectType.HASH:
        return eval_hash_index_expression(left, index)
    else:
        return new_error(f"index operator not supported: {left.type().value}")


def eval_array_index_expression(array: Object, index: Object) -> Null | Object:
    assert isinstance(array, Array)
    assert isinstance(index, Integer)
    idx = index.value
    max_idx = len(array.elements) - 1
    if idx < 0 or idx > max_idx:
        return NULL
    return array.elements[idx]


def eval_hash_literal(node: HashLiteral, env: Environment) -> Error | Hash:
    pairs: dict[HashKey, HashPair] = {}
    for key_node, value_node in node.pairs.items():
        key: Object = evaluate(key_node, env)
        if is_error(key):
            assert isinstance(key, Error)
            return key
        if not isinstance(key, Hashable):
            return new_error(f"unusable as hash key: {key.type().value}")
        value: Object = evaluate(value_node, env)
        if is_error(value):
            assert isinstance(value, Error)
            return value
        hashed: HashKey = key.hash_key()
        pairs[hashed] = HashPair(key, value)
    return Hash(pairs)


def eval_hash_index_expression(hash_obj: Object, index: Object) -> Error | Null | Object:
    assert isinstance(hash_obj, Hash)
    if not isinstance(index, Hashable):
        return new_error(f"unusable as hash key: {index.type().value}")
    pair: HashPair | None = hash_obj.pairs.get(index.hash_key())
    if not pair:
        return NULL
    return pair.value


# The eval function must be at the end as it references many other functions
def evaluate(node: Node, env: Environment) -> Object | Error | Null:
    if isinstance(node, Program):
        return eval_program(node, env)
    elif isinstance(node, BlockStatement):
        return eval_block_statement(node, env)
    elif isinstance(node, ExpressionStatement):
        return evaluate(node.expression, env)
    elif isinstance(node, ReturnStatement):
        val: Object = evaluate(node.return_value, env)
        if is_error(val):
            assert isinstance(val, Error)
            return val
        return ReturnValue(val)
    elif isinstance(node, LetStatement):
        val: Object = evaluate(node.value, env)  # type: ignore
        if is_error(val):
            assert isinstance(val, Error)
            return val
        env.set(node.name.value, val)
    elif isinstance(node, IntegerLiteral):
        return Integer(node.value)
    elif isinstance(node, StringLiteral):
        return String(node.value)
    elif isinstance(node, BooleanLiteral):
        return native_bool_to_boolean_object(node.value)
    elif isinstance(node, PrefixExpression):
        right = evaluate(node.right, env)
        if is_error(right):
            assert isinstance(right, Error)
            return right
        return eval_prefix_expression(node.operator, right)
    elif isinstance(node, InfixExpression):
        left = evaluate(node.left, env)
        if is_error(left):
            assert isinstance(left, Error)
            return left
        right: Object | Error | Null = evaluate(node.right, env)  # type: ignore
        if is_error(right):
            assert isinstance(right, Error)
            return right
        return eval_infix_expression(node.operator, left, right)
    elif isinstance(node, IfExpression):
        return eval_if_expression(node, env)
    elif isinstance(node, Identifier):
        return eval_identifier(node, env)
    elif isinstance(node, FunctionLiteral):
        params: list[Identifier] = node.parameters
        body: BlockStatement = node.body
        return Function(params, body, env)
    elif isinstance(node, CallExpression):
        function: Object = evaluate(node.function, env)
        if is_error(function):
            assert isinstance(function, Error)
            return function
        args: list[Object] = eval_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]
        return apply_function(function, args)
    elif isinstance(node, ArrayLiteral):
        elements: list[Object] = eval_expressions(node.elements, env)
        if len(elements) == 1 and is_error(elements[0]):
            return elements[0]
        return Array(elements)
    elif isinstance(node, IndexExpression):
        left: Object = evaluate(node.left, env)  # type: ignore
        if is_error(left):
            assert isinstance(left, Error)
            return left
        index: Object = evaluate(node.index, env)
        if is_error(index):
            assert isinstance(left, Error)
            return index
        return eval_index_expression(left, index)
    elif isinstance(node, HashLiteral):
        return eval_hash_literal(node, env)
    return Null()
