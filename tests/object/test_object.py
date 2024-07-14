from src.object.object import Boolean, Integer, String


def test_string_hash_key():
    hello1 = String("Hello World")
    hello2 = String("Hello World")
    diff1 = String("My name is johnny")
    diff2 = String("My name is johnny")

    assert hello1.hash_key() == hello2.hash_key()
    assert diff1.hash_key() == diff2.hash_key()
    assert hello1.hash_key() != diff1.hash_key()


def test_boolean_hash_key():
    true1 = Boolean(True)
    true2 = Boolean(True)
    false1 = Boolean(False)
    false2 = Boolean(False)

    assert true1.hash_key() == true2.hash_key()
    assert false1.hash_key() == false2.hash_key()
    assert true1.hash_key() != false1.hash_key()


def test_integer_hash_key():
    one1 = Integer(1)
    one2 = Integer(1)
    two1 = Integer(2)
    two2 = Integer(2)

    assert one1.hash_key() == one2.hash_key()
    assert two1.hash_key() == two2.hash_key()
    assert one1.hash_key() != two1.hash_key()
