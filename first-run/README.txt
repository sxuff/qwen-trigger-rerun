Qwen3.8-Flash-Next behavioral probe — GX10, 2026-10-26

The current report is docs/index.html at the repository root; this run is described there under "Earlier runs".

Study scope
  - 600 recovered TensorFold prefill completions, recounted from raw text.
  - 200 controlled TensorFold + 200 controlled Flare completions.
  - 2 saved TensorFold Docker trajectories, each bounded at 12 turns.
  - Interrupted, truncated, mock and initial-default pilot data are kept separately;
    they are not silently pooled into the completed controlled comparison.

Reproduce the controlled prefill (on a machine with Python 3 and Jinja2,
and the chosen model already served at the specified local endpoint):

  python3 inputs/fetch_article_inputs.py
  cd scripts
  python3 controlled_prefill.py --base http://127.0.0.1:8001 \
    --model qwen38-flash-next-tf405 --template ../inputs/chat_template.jinja \
    --blocks ../inputs/article-code-blocks.json --out ../new-tensorfold --samples 25

For the prepared Flare build, use its local port 8000 and --model flare.
The probe never executes its generated completions.
Server configuration, package identity, sampling constraints and hashes are in
environment/. Both runtime builds must use the recorded quantized weights for
a comparable reproduction; this is not a test of runtime alone.

Recompute the saved summaries (no model needed):
  python3 scripts/analyze_probe.py --root raw/runs --out recomputed

The original probe_harness.py is retained for provenance and supplies the prompt
template helper imported by controlled_prefill.py. Its header predates Docker
mode and is inaccurate about all modes being mock-only. audited_probe_harness.py
corrects that documentation, verifies sandbox configuration, logs full tool
results, checkpoints completed turns and labels termination reasons.

Source: https://cohere.com/blog/concerning-behaviour-popular-open-weight-ai-model
Published input excerpts can be fetched directly using the helper in inputs/;
their hashes are included, rather than redistributing the article's prose.
Published-excerpt fields in exported manifests are source/hash references;
model responses and prompt hashes are preserved unchanged.
The complete original Cohere system/tool configuration was not published, so
these experiments are adapted reconstructions, not exact replications.

Environment receipts show TensorFold was restored after the Flare comparison.
SHA256SUMS lists hashes of every included file except itself.

Public copy: the local username, hostname and one working-directory name are
replaced with <user>, <host> and <workspace>, and containers unrelated to the
study are omitted from the environment receipts. Model outputs are unchanged;
they contain hostnames, IPs and URLs the model generated. Treat them as data
and do not visit them.
