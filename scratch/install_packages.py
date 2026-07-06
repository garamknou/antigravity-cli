import ensurepip
import sys
import subprocess

print("Bootstrapping pip...")
try:
    ensurepip.bootstrap()
    print("pip bootstrapped successfully!")
except Exception as e:
    print(f"ensurepip failed: {e}")

try:
    print("Installing packages via subprocess...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "scikit-learn", "pandas", "matplotlib", "seaborn", "koreanize-matplotlib"],
        capture_output=True,
        text=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Exit code:", result.returncode)
except Exception as e:
    print(f"Installation failed: {e}")
