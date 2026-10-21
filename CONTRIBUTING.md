# Contributing

This is a tutorial for beginners. Keep every lesson aimed at a reader who has
never used a terminal, Python or a remote computer.

- Use only public datasets for the worked examples, and cite them.
- Do not commit addresses or names of private machines or networks, private
  keys, tokens, or other people's accounts. The tests look for them.
- Every lesson ends with "You should now see" and a three-row
  "Troubleshooting" table.
- Do not commit model weights, checkpoints, downloaded data, or tokenized
  datasets.
- Keep code blocks runnable as written, and state in the text what has and has
  not been run, on which machine, and when (use UTC or ISO dates).
- The quickstart pins Geneformer to one commit and its Python packages in
  `quickstart/uv.lock`. Change them together, rerun the quickstart from a
  clean folder, and update the measured numbers in the README.

Before opening a pull request:

```bash
pip install pytest
pytest
```

The tests syntax-check every Python and Bash block, confirm that relative
links resolve, check each lesson's closing sections, and look for secrets,
private-network addresses and personal paths.
