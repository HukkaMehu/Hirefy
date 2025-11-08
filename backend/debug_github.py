from services.github_api import analyze_github_profile
import traceback

try:
    print("Fetching torvalds GitHub profile...")
    data = analyze_github_profile('torvalds')
    print(f"Result: {data}")
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()
