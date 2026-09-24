import pytest
from src.utils.storage import validate_file, sanitize_filename

def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("my receipt (1).jpg") == "my_receipt__1_.jpg"
    assert sanitize_filename("normal_file.png") == "normal_file.png"

def test_validate_file_valid_png():
    # Fake PNG signature
    fake_png = b'\x89PNG\r\n\x1a\n' + b'fake body'
    is_valid, ext = validate_file(fake_png, "test.png")
    assert is_valid == True
    assert ext == ".png"

def test_validate_file_valid_jpeg():
    fake_jpg = b'\xff\xd8\xff' + b'fake body'
    is_valid, ext = validate_file(fake_jpg, "test.jpeg")
    assert is_valid == True
    assert ext == ".jpeg"

def test_validate_file_invalid_ext():
    is_valid, msg = validate_file(b'fake body', "test.txt")
    assert is_valid == False
    assert "Unsupported" in msg

def test_validate_file_invalid_signature():
    is_valid, msg = validate_file(b'fake body', "test.jpg")
    assert is_valid == False
    assert "Invalid image signature" in msg

def test_validate_file_valid_pdf():
    fake_pdf = b'%PDF-1.4\n' + b'fake body'
    is_valid, ext = validate_file(fake_pdf, "test.pdf")
    assert is_valid == True
    assert ext == ".pdf"
