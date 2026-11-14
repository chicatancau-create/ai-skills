"""Pre-seed the Kompress ONNX model + ModernBERT tokenizer into the HF cache.

Why: headroom's ML compressor (Kompress) is what produces the big JSON/log
savings. It is currently disabled because HEADROOM_OFFLINE=1 refuses to fetch
the model, and huggingface.co is unreachable from this machine anyway.
hf-mirror.com IS reachable.

headroom/onnx_runtime.py:146 tries local_files_only=True FIRST and only guards
the network fallback, so a pre-seeded cache works with HEADROOM_OFFLINE=1 left on.
Revisions below are headroom's own pinned SHAs (supply-chain integrity).
"""
import io
import os
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ.pop("HEADROOM_OFFLINE", None)
os.environ.setdefault("HF_HOME", r"D:\uv\data\huggingface")
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import hf_hub_download  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

print("HF_ENDPOINT = %s" % os.environ["HF_ENDPOINT"])
print("HF_HOME     = %s" % os.environ["HF_HOME"], flush=True)

KOMPRESS_REPO = "chopratejas/kompress-v2-base"
KOMPRESS_REV = "b1563631b35bfdcee37587ad530147497d820d4c"
ONNX_FILE = "onnx/kompress-int8-wo.onnx"          # 261MB, fp32-equivalent f1
BERT_REPO = "answerdotai/ModernBERT-base"
BERT_REV = "8949b909ec900327062f0ebf497f51aef5e6f0c8"

print("\n=== 1/2 Kompress ONNX weights (%s) ===" % ONNX_FILE, flush=True)
t0 = time.time()
try:
    p = hf_hub_download(KOMPRESS_REPO, ONNX_FILE, revision=KOMPRESS_REV)
    print("  OK  %.1fs  %s" % (time.time() - t0, p))
    print("  size = %.1f MB" % (os.path.getsize(p) / 1048576.0), flush=True)
except Exception as e:
    print("  FAIL %.1fs  %r" % (time.time() - t0, e), flush=True)

print("\n=== 2/2 ModernBERT tokenizer ===", flush=True)
t0 = time.time()
try:
    tok = AutoTokenizer.from_pretrained(BERT_REPO, revision=BERT_REV)
    print("  OK  %.1fs  %s  vocab=%d" % (time.time() - t0, type(tok).__name__, len(tok)), flush=True)
except Exception as e:
    print("  FAIL %.1fs  %r" % (time.time() - t0, e), flush=True)

print("\n=== verify: cache-only lookup must now succeed (this is what the proxy does) ===", flush=True)
try:
    p = hf_hub_download(KOMPRESS_REPO, ONNX_FILE, revision=KOMPRESS_REV, local_files_only=True)
    print("  ONNX cache HIT      : %s" % p)
except Exception as e:
    print("  ONNX cache MISS     : %r" % e)
try:
    tok = AutoTokenizer.from_pretrained(BERT_REPO, revision=BERT_REV, local_files_only=True)
    print("  tokenizer cache HIT : %s" % type(tok).__name__)
except Exception as e:
    print("  tokenizer cache MISS: %r" % e)
