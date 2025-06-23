import os
import subprocess
import shutil
from beartype import beartype

@beartype
def download_simkgc_data(data_dir_name: str = "text_based_kgc_data"):
    repo_url = "https://github.com/intfloat/SimKGC.git"
    clone_dir = "SimKGC"

    # 1. Clone the repository if not already present
    if not os.path.exists(clone_dir):
        print(f"Cloning {repo_url} ...")
        subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
    else:
        print(f"{clone_dir} already exists, skipping clone.")

    # 2. Download data by running the script
    script_path = os.path.join(clone_dir, "scripts", "download_wikidata5m.sh")
    if os.path.exists(script_path):
        print(f"Making {script_path} executable ...")
        os.chmod(script_path, 0o755)
        print(f"Running scripts/download_wikidata5m.sh in {clone_dir} ...")
        try:
            proc = subprocess.Popen(["bash", "scripts/download_wikidata5m.sh"], cwd=clone_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                print(line, end="")
            proc.wait()
            if proc.returncode != 0:
                print(f"[ERROR] Script failed with exit code {proc.returncode}")
                return
        except Exception as e:
            print(f"[ERROR] Exception while running script: {e}")
            return
    else:
        print(f"Script {script_path} not found!")
        return

    # 3. Rename data directory to `text_based_kgc_data` and move it outside SimKGC
    src_data_dir = os.path.join(clone_dir, "data")
    dest_data_dir = os.path.abspath(os.path.join(clone_dir, "..", data_dir_name))
    if os.path.exists(src_data_dir):
        if os.path.exists(dest_data_dir):
            print(f"{dest_data_dir} already exists, skipping move.")
        else:
            print(f"Moving {src_data_dir} to {dest_data_dir} ...")
            shutil.move(src_data_dir, dest_data_dir)
    else:
        print(f"Data directory {src_data_dir} not found!")

    # 4. Delete the SimKGC folder
    print(f"Deleting {clone_dir} ...")
    shutil.rmtree(clone_dir)

if __name__ == "__main__":
    download_simkgc_data()

