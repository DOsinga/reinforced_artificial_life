from pathlib import Path

VIEW_DISTANCE = 1

EPISODE_FILE = 'episode.jsonl'
HISTORY_FILE = 'history.jsonl'
WEIGHTS_FILE = 'model_weights.h5'

script_path = Path(__file__).resolve().parent.parent
state_pattern = str(script_path / 'state' / 'last_{filename}')
