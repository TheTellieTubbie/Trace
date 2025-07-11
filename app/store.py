seen_chunks = {}

def is_previously_seen(hash_val):
    return hash_val in seen_chunks

def add_chunk(hash_val, metadata):
    seen_chunks[hash_val] = metadata


