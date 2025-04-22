import os
import json
import glob

from tqdm import tqdm
from src.models.db import local_session, Chat
from src.models.signal import Envelope

def add_envelope_to_db(envelope: Envelope, cursor):
    msg = Chat(
        chat_id=envelope.chat_id(),
        message=envelope.get_message().message,
        envelope=envelope.model_dump()
    )
    cursor.add(msg)

def process_jsonl_file(file_path, cursor):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                try:
                    envelope = Envelope.model_validate_json(line)
                except:
                    envelope = Envelope.model_validate_json(json.loads(line))
                
                add_envelope_to_db(envelope, cursor)

            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in file: {file_path}")

def process_all_jsonl_files(base_dir):
    for root, _, files in os.walk(base_dir):

        for file in tqdm(files):
            cursor = local_session()
            if file.endswith('.jsonl'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                process_jsonl_file(file_path, cursor)
            cursor.commit()
            cursor.close()

def process_line(line: str, cursor):
    pattern = 'ERROR - Validation error:'
    position = line.find(pattern)

    if position == -1:
        return
    
    line = line[position + len(pattern):].strip()
    try:
        data = json.loads(line)
        envelope = Envelope.model_validate(data.get('envelope'))
    except:
        return

    add_envelope_to_db(envelope, cursor)

def process_file(file, cursor):
    with open(file, 'r', encoding='utf-8') as f:
        [process_line(line, cursor) for line in f]

def process_errors_from_logs(base_dir):
    cursor = local_session()

    for root, _, files in os.walk(base_dir):
        for file in tqdm(files):
            if not file.endswith('.log'):
                continue

            file_path = os.path.join(root, file)
            print(f"Processing log file: {file_path}")

            process_file(file_path, cursor)
            cursor.commit()
    cursor.close()

def main():
    base_dir = '/home/azureuser/data'
    process_all_jsonl_files(base_dir)

    base_dir = '/home/azureuser/.logs'
    process_errors_from_logs(base_dir)

if __name__ == '__main__':
    main()