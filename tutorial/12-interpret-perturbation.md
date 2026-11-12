# Lesson 12. Interpret perturbation results

In [lesson 11](11-run-perturbation.md) you compared original and edited
embeddings for one gene in a small PBMC pilot. This lesson teaches how to read
that result and how to interpret a **different**, goal-directed analysis.
All numerical examples below are invented, not output from the pilot or a
real study. The available columns and signs depend on the Geneformer revision
and analysis mode: inspect the [official statistics documentation](https://geneformer.readthedocs.io/en/latest/geneformer.in_silico_perturber_stats.html)
and installed source before interpreting your own files.

## 1. Ask what was compared

| Mode | Question | A higher value means |
| --- | --- | --- |
| Original versus edited cosine | How similar are the two cell embeddings? | More similar directions; no direction toward a goal is given |
| Goal-directed cosine change | Did similarity to a specified reference increase after the edit? | For the simple difference defined below, more movement toward that reference |
| Gene embedding change | Which remaining gene representations changed? | Depends on the metric; it is not an expression fold change |

For example, original-versus-edited cosine of 0.98 is more similar than 0.90.
Neither value says whether a cell became healthier. The cosine measures an
angle in an embedding space, not a clinical score.

## 2. Work through a goal-directed example

Suppose the same gene edit is applied to a DCM cardiomyocyte and a non-failing
reference centroid is held fixed. Define a simple teaching metric:

`goal shift = cosine(edited, goal) - cosine(original, goal)`

| Quantity | Invented value |
| --- | ---: |
| Original-to-goal similarity | 0.50 |
| Edited-to-goal similarity | 0.56 |
| Goal shift | +0.06 |

Under **this explicitly defined metric**, +0.06 indicates increased similarity
to the chosen reference; -0.06 would indicate decreased similarity. It is not
6% recovery, does not prove better contraction, and may coexist with an
undesirable shift toward another state. Geneformer's own output can use a
specific definition, averaging and sign convention: do not assume every CSV
column implements this exact formula.

To check the arithmetic in a terminal with Python installed:

```python
original_to_goal = 0.50
edited_to_goal = 0.56
shift = edited_to_goal - original_to_goal
print(f"Illustrative goal shift: {shift:+.2f}")
```

This prints `Illustrative goal shift: +0.06`. It does not load model results.

## 3. Read a fictional result table

| Candidate | Cells detected | Donors represented | Mean donor-level goal shift | FDR | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Gene A | 600 | 6 | +0.06 | 0.02 | Candidate for follow-up if the null and donor analysis were valid |
| Gene B | 900 | 1 | +0.09 | 0.001 | Large cell count, but donor replication is missing |
| Gene C | 500 | 5 | -0.04 | 0.03 | In this example, movement away from the defined goal |

These are illustrative summaries, not Geneformer output. An FDR is meaningful
only relative to its statistical test, null, and family of comparisons. Many
cells from one donor do not substitute for independent donors; a cell-level
p-value or correction alone does not solve donor dependence. A significant
result is not necessarily a large, reproducible or clinically useful effect.

The official `goal_state_shift` statistics can report `N_Detections`,
`Shift_to_goal_end`, `Shift_to_alt_end`, and `Goal_end_FDR`. They need not all
appear in every output. `N_Detections` counts eligible cells, not donors.
The built-in random comparison is not automatically matched for gene
expression or detection. Consult your installed version for the precise test
and conventions. A singleton pilot does not provide a gene-wide comparison.

## 4. Apply a checklist before prioritizing

1. **Dataset:** What cell type, disease, batch, tissue and treatment were used?
   Is condition confounded with donor, study or assay?
2. **Reference:** Were goal and alternate centroids defined from comparable
   cells with the same checkpoint, layer and embedding mode? Were they fixed
   before evaluating test donors?
3. **Edit:** Was one gene deleted or moved to the front? Were multiple genes
   passed as a combined list? How many cells and donors contained each gene?
4. **Evidence:** Are effects consistent across donors, robust to reference
   choice and compared with suitable matched controls and simple baselines?
   Is the test and multiple-testing family stated?
5. **Validation:** Were candidates selected on development data evaluated in
   held-out donors or an independent cohort? What real perturbation and
   functional measurements could confirm or refute the prediction?

A goal centroid can hide variation among cells. A state may look separable
because of batch. Low-detection genes can be tested in a selected subset of
cells. Interpret all of these before interpreting the ranking.

## 5. Translate to blood and heart

For PBMCs, compare stimulated and resting **within one immune cell type** and
keep paired samples from each donor in the same split. A shift toward resting
is not automatically desirable immunosuppression. The standard PBMC 3k dataset
has neither a stimulated/resting comparison nor donor replication.

For cardiomyocytes, compare a well-defined DCM or HCM start state with a
comparable non-failing reference; check shifts toward alternative states too.
A model-predicted shift is a candidate for testing, not a measurement of
contractility or clinical benefit. See the [blood](perturbation-peripheral-blood.md)
and [heart](perturbation-cardiomyocytes.md) design lessons.

## You should now see

Why the lesson 11 pilot reports general embedding similarity, how an
illustrative goal-directed score differs, and what evidence is needed before
interpreting any candidate biologically.

## Troubleshooting

| You see | What to do |
| --- | --- |
| `Cosine_sim_mean` but no `Shift_to_goal_end` | The pilot compared original and edited embeddings without a goal; do not infer a goal shift |
| A goal shift whose sign is unfamiliar | Read the installed version's implementation and define the comparison explicitly |
| A very low FDR from one donor | Report the limited donor replication; obtain independent donors |
| A different CSV column name | Identify the software revision and stats mode before mapping the field |

Previous: [11. Run a first perturbation](11-run-perturbation.md) · Back to [start](00-start-here.md)
