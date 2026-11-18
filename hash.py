from werkzeug.security import generate_password_hash
# Genera un hash con un formato más compatible y seguro
nuevo_hash = generate_password_hash(input('Nueva contraseña: '), method='pbkdf2:sha256')
print("\nCopia este hash completo:")
print(nuevo_hash)