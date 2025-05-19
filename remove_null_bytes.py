# filepath: remove_null_bytes.py
import os

def remove_null_bytes(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    
                    content = content.replace(b'\x00', b'')
                    
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    print(f"Bytes nulos eliminados de {filepath}")
                except Exception as e:
                    print(f"Error al procesar {filepath}: {e}")

if __name__ == "__main__":
    directory = "src"
    remove_null_bytes(directory)