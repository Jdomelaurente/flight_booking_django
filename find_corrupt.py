import os

def find_corrupt_files(root_dir):
    corrupt_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'rb') as f:
                        if b'\x00' in f.read():
                            corrupt_files.append(filepath)
                except Exception as e:
                    print(f"Could not read {filepath}: {e}")
    return corrupt_files

if __name__ == "__main__":
    target_dir = r"c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend"
    print(f"Scanning {target_dir} for corrupt .py files...")
    corrupt = find_corrupt_files(target_dir)
    if corrupt:
        print("Found corrupt files:")
        for f in corrupt:
            print(f)
    else:
        print("No corrupt .py files found.")
