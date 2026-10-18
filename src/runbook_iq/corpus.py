"""Deterministic, section-aware canonical chunks; no inference side effects."""
import hashlib
import json
import re
from pathlib import Path
import yaml
from pydantic import Field
from .schemas import Chunk, Record
from .tokenization import REVISION

class CorpusSnapshot(Record):
    version: str
    chunks: list[Chunk]
    source_hashes: dict[str, str]
    fingerprint: str

def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(text)
    temporary.replace(path)

def fence_marker(line):
    return re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)

def closes_fence(mark, fence):
    return mark and mark.group(1)[0] == fence[0] and len(mark.group(1)) >= len(fence) and not mark.group(2).strip()

def sections(body):
    title = 'Overview'
    lines = []
    fence = None
    for line in body.splitlines():
        mark = fence_marker(line)
        if mark:
            token = mark.group(1)
            if fence is None: fence = token
            elif closes_fence(mark, fence): fence = None
        heading = re.match(r'^#{1,6}\s+(.+)', line) if fence is None and not mark else None
        if heading:
            if '\n'.join(lines).strip(): yield title, '\n'.join(lines).strip()
            title, lines = heading.group(1), []
        else: lines.append(line)
    if fence: raise ValueError('Unclosed fenced code block')
    if '\n'.join(lines).strip(): yield title, '\n'.join(lines).strip()

def blocks(body):
    # Use the same fence grammar as sections; a shorter embedded fence is data.
    lines, fence = [], None
    for line in body.splitlines():
        mark = fence_marker(line)
        if fence is not None:
            lines.append(line)
            if closes_fence(mark, fence):
                yield '\n'.join(lines)
                lines, fence = [], None
        elif mark:
            if lines: yield '\n'.join(lines)
            lines, fence = [line], mark.group(1)
        elif not line.strip():
            if lines: yield '\n'.join(lines)
            lines = []
        else: lines.append(line)
    if fence: raise ValueError('Unclosed fenced code block')
    if lines: yield '\n'.join(lines)

def build_corpus(source_dir, settings, counter):
    chunks, hashes, seen = [], {}, set()
    fingerprint = digest({'splitter': 'sections-v2', 'tokenizer': REVISION,
                          'target': settings.chunk_target_tokens, 'max': settings.embedding_max_tokens})
    for path in sorted(Path(source_dir).glob('*.md')):
        raw = path.read_text().replace('\r\n', '\n')
        if not raw.startswith('---\n'): raise ValueError(f'{path}: missing metadata')
        _, front, body = raw.split('---', 2)
        meta = yaml.safe_load(front)
        required = ['document_id', 'title', 'service', 'document_type', 'revision']
        if not isinstance(meta, dict) or not all(isinstance(meta.get(k), str) for k in required):
            raise ValueError(f'{path}: invalid metadata')
        doc = meta['document_id']
        if doc in seen: raise ValueError(f'Duplicate document ID: {doc}')
        seen.add(doc); hashes[doc] = digest(raw)
        for section, text in sections(body):
            header = f"{meta['title']} | {section}\n"
            if counter.count(header) >= settings.chunk_target_tokens:
                raise ValueError(f'{path}: heading too large')
            pieces, current = [], ''
            for block in blocks(text):
                block = block.strip()
                if not block: continue
                rendered = header + block
                if block.startswith(('```', '~~~')):
                    if counter.count(rendered) > settings.embedding_max_tokens:
                        raise ValueError(f'{path}/{section}: oversized fenced block; edit source')
                    if current: pieces.append(current); current = ''
                    pieces.append(block); continue
                remaining = block
                while remaining:
                    proposed = (current + '\n\n' + remaining).strip()
                    if counter.count(header + proposed) <= settings.chunk_target_tokens:
                        current = proposed; break
                    if current: pieces.append(current); current = ''; continue
                    low, high = 1, len(remaining)
                    while low < high:
                        mid = (low + high + 1) // 2
                        if counter.count(header + remaining[:mid]) <= settings.chunk_target_tokens: low = mid
                        else: high = mid - 1
                    cut = remaining.rfind(' ', 0, low + 1)
                    if cut <= 0: cut = low
                    pieces.append(remaining[:cut]); remaining = remaining[cut:].lstrip()
            if current: pieces.append(current)
            for number, piece in enumerate(pieces):
                rendered = header + piece
                if counter.count(rendered) > settings.embedding_max_tokens: raise ValueError('Chunk exceeds model bound')
                content_hash = digest({'metadata': meta, 'section': section, 'text': rendered})
                chunk_id = 'c-' + digest([doc, section, number, content_hash])[:24]
                chunks.append(Chunk(chunk_id=chunk_id, text=rendered, section=section,
                    content_hash=content_hash, corpus_version='', **{k: meta[k] for k in required},
                    environment=meta.get('environment')))
    if not chunks: raise ValueError('Corpus has no usable documents')
    version = digest([hashes, fingerprint])
    for chunk in chunks: chunk.corpus_version = version
    return CorpusSnapshot(version=version, chunks=chunks, source_hashes=hashes, fingerprint=fingerprint)

def write_snapshot(snapshot, output_dir):
    output_dir = Path(output_dir)
    atomic_write(output_dir / 'chunks.jsonl', ''.join(c.model_dump_json() + '\n' for c in snapshot.chunks))
    atomic_write(output_dir / 'candidate.json', snapshot.model_dump_json(indent=2))

def read_snapshot(path):
    return CorpusSnapshot.model_validate_json(Path(path).read_text())
