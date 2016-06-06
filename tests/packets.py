import sys

sys.stdout.write(b"\x00\x00\x00\x01\x01".decode("utf-8"))
sys.stdout.write(b"\x00\x00\x00\x02\x01\x01".decode("utf-8"))
sys.stdout.write(b"\x00\x00\x00\x03\x01\x02\x01".decode("utf-8"))
sys.stdout.write(b"\x00\x00\x00\x04\x01\x01\x01\x01".decode("utf-8"))
sys.stdout.write(b"\x00\x00\x00".decode("utf-8"))
