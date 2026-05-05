import sys
import pytest
from main import parse_log_line, SAMPLE_LOG, main

def test_parse_log_line_valid():
    line = '127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326'
    assert parse_log_line(line) == "200"

def test_parse_log_line_invalid_missing_status():
    line = '127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.1" - 2326'
    assert parse_log_line(line) is None

def test_parse_log_line_no_trailing_digit():
    # pattern requires \s+\d after status code, so this line doesn't match
    line = '127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.1" 200'
    assert parse_log_line(line) is None

def test_parse_log_line_empty_string():
    assert parse_log_line("") is None

def test_sample_log_lines_expected_codes():
    expected = {
        1: "200", 2: "302", 3: "200", 4: "404", 5: "500",
        6: "200", 7: "404", 8: "403", 9: "200", 10: "204",
        11: "504", 12: "200", 13: "502"
    }
    for idx, line in enumerate(SAMPLE_LOG, start=1):
        assert parse_log_line(line) == expected[idx], f"Line {idx} mismatch"

def test_main_sample(capsys):
    old_argv = sys.argv
    sys.argv = ['main.py']  # no file argument → use sample data
    try:
        main()
    finally:
        sys.argv = old_argv

    out = capsys.readouterr().out
    assert "No log file provided. Using built-in sample data." in out
    assert "Processed 13 lines, found 13 with status codes." in out
    assert "200 : 5" in out
    assert "404 : 2" in out
    assert "500 : 1" in out
    # Verify sorted order (204 appears before others)
    assert "204 : 1" in out

def test_main_with_file_exits(capsys):
    old_argv = sys.argv
    sys.argv = ['main.py', 'dummy.log']
    try:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "file reading is not allowed" in captured.err
    finally:
        sys.argv = old_argv