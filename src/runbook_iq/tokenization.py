"""Pinned tokenizer assets only; never loads model weights or remote code."""
import hashlib
import json
from pathlib import Path
from typing import Protocol
from tokenizers import Tokenizer

MODEL = 'nvidia/llama-nemotron-embed-1b-v2'
REVISION = '113abe4acafa848e77ead9c0623205e511932348'

class TokenCounter(Protocol):
    def count(self, text: str) -> int: ...

class EmbeddingTokenizer:
    def __init__(self, path: Path):
        self.tokenizer = Tokenizer.from_file(str(path))
        self.tokenizer.no_truncation()
        self.tokenizer.no_padding()
    def count(self, text: str) -> int:
        # Count the longer passage prefix plus BOS/EOS safety room.
        return len(self.tokenizer.encode('passage: ' + text).ids) + 8

def load_embedding_tokenizer(settings):
    root = settings.runtime_dir / 'tokenizer'
    identity = json.loads((root / 'identity.json').read_text())
    if identity != {'model': MODEL, 'revision': REVISION}:
        raise ValueError('Tokenizer identity mismatch; run tokenizer setup')
    return EmbeddingTokenizer(root / 'tokenizer.json')

def setup_tokenizer(settings):
    from huggingface_hub import hf_hub_download
    import shutil
    root = settings.runtime_dir / 'tokenizer'
    root.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(MODEL, 'tokenizer.json', revision=REVISION,
                          cache_dir=settings.runtime_dir / 'hf-cache')
    shutil.copyfile(path, root / 'tokenizer.json')
    (root / 'identity.json').write_text(json.dumps({'model': MODEL, 'revision': REVISION}))
