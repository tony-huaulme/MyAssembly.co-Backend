import os
secret_key = os.urandom(24).hex()  # 24 bytes (192 bits) is a good size
print(secret_key)