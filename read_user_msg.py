import json
import sys

# Configure stdout to use utf-8 to avoid encoding errors on windows console
sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\biyan\.gemini\antigravity-ide\brain\56e4ec55-69e4-46f6-8f31-b3337826786c\.system_generated\logs\transcript.jsonl"

try:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                data = json.loads(line)
                step = data.get('step_index')
                source = data.get('source')
                type_ = data.get('type')
                
                # Check if it's a user message
                if source == 'USER_EXPLICIT' or type_ == 'USER_INPUT':
                    content = data.get('content', '')
                    # Check if reviews or comments are mentioned
                    print(f"--- STEP {step} ---")
                    print(content.strip())
                    print("-" * 40)
            except Exception as inner_err:
                print(f"Error parsing line {line_num}: {inner_err}")
except Exception as e:
    print("Error opening log file:", e)
