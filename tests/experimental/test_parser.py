from kor.experimental.tokenizer import tokenize


def test_tokenize():
    assert tokenize("(+ 1 2)") == [
        ("open_paren", "("),
        ("symbol", "+"),
        ("number", "1"),
        ("number", "2"),
        ("close_paren", ")"),
    ]

    assert tokenize("(add (sub 1 2) 3)") == [
        ("open_paren", "("),
        ("symbol", "add"),
        ("open_paren", "("),
        ("symbol", "sub"),
        ("number", "1"),
        ("number", "2"),
        ("close_paren", ")"),
        ("number", "3"),
        ("close_paren", ")"),
    ]

    assert tokenize('(concat "hello" "world")') == [
        ("open_paren", "("),
        ("symbol", "concat"),
        ("string", '"hello"'),
        ("string", '"world"'),
        ("close_paren", ")"),
    ]
    
