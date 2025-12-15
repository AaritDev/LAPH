from core.repair_loop import RepairLoop


def test_sanitize_injects_imports_and_seed():
    rl = RepairLoop(None)
    # code uses re and randint but lacks imports
    code = "def roll_dice(input_line):\n    parts = re.match(r'(\\d*)d(\\d+)', '3d6')\n    x = randint(1,6)\n    return x"
    tests = "assert roll_dice('3d6') >= 1"

    preamble, c, t = rl._sanitize_code_for_run(code, tests)
    assert 'import re' in preamble
    assert 'import random' in preamble
    assert 'random.seed(0)' in preamble

    # Running the full payload should not raise NameError for re or randint
    full = preamble + c + "\n\n" + t
    stdout, stderr, exitcode = rl.runner.run_code(full)
    assert 'NameError' not in stderr


def test_sanitizer_prevents_nameerror_with_coder_style_tests():
    rl = RepairLoop(None)
    # coder wrote asserts with fixed totals (nondeterministic without seeding)
    code = "def roll_dice(input_line):\n    parts = re.match(r'(\\d*)d(\\d+)', '3d6')\n    x = randint(1,6) + randint(1,6) + randint(1,6)\n    return x"
    tests = "assert roll_dice('3d6') == 9"
    preamble, c, t = rl._sanitize_code_for_run(code, tests)
    full = preamble + c + "\n\n" + t
    stdout, stderr, exitcode = rl.runner.run_code(full)
    # Should not error with NameError (might still fail assertion)
    assert 'NameError' not in stderr
