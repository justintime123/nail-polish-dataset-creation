from pathlib import Path

#https://www.reddit.com/r/learnpython/comments/182b4ty/paths_class/
ROOT_PATH = Path(__file__).parent
DATA_PATH = ROOT_PATH / "data"
DATA_STEP_1 = DATA_PATH / "step_1"
DATA_STEP_2 = DATA_PATH / "step_2"
PROCESSED_DATA_PATH = DATA_PATH / "processed" / "data.parquet"