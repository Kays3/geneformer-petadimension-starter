# Perturbation lesson: peripheral blood immune cells

This lesson extends the [paper-aligned guide](paper-pipeline.md) with a
peripheral blood example. It is a **study design and interpretation exercise**;
no new perturbation experiment has been run or validated for this lesson.
Start with [data preparation](05-prepare-data.md), [tokenization](06-tokenize.md),
[embeddings](07-embeddings.md) and [classification](08-classify.md).

## The question

Suppose you have paired resting and stimulated peripheral blood mononuclear
cells (PBMCs) from multiple donors. Within CD8 T cells, which single-gene
input deletions shift the model representation of stimulated cells toward a
resting reference? The reverse question—resting toward stimulated—is different.
This design concerns a specific assay and time point; resting is not inherently
healthier, and altered similarity does not establish immunosuppression.

The PBMC 3k dataset in this repository has **one donor and no paired
resting/stimulated conditions**. It can teach preprocessing and exercise the
mechanics of embeddings, but cannot answer this question, construct a real
activation goal, or provide donor-level replication. You need an independent,
properly labeled multi-donor dataset to perform the study. The published
[immune perturbation study and tutorial](https://github.com/bicklab/geneformer)
provide a relevant example of resting and stimulated PBMCs; its experimental
setup and training approach are distinct from this hypothetical exercise.

## Step 1. Prepare the comparison

| Decision | Example | Reason |
| --- | --- | --- |
| Cell population | CD8 T cells, annotated consistently | Different immune lineages have different baseline programs |
| Start / goal | Stimulated / resting | Defines the direction of the question |
| Experimental unit | Donor, with both conditions when available | Cells from a donor are correlated |
| Split | Hold out entire donors | Paired samples from the same donor must stay together |
| Covariates | Assay, batch, donor, stimulation, time, treatment, QC | They may explain apparent condition differences |
| Reference | Resting CD8 T-cell embedding centroid from development donors | A reproducible target for goal-directed shifts |

Check donor-by-condition-by-cell-type counts before training, and document
missing pairs. A condition measured only in one batch cannot be separated
reliably from that batch. Confirm whether the dataset was used to develop the
model or tune decisions if an independent evaluation is claimed. Retain raw
counts and Ensembl IDs and record cell IDs, condition, donor, and batch through
tokenization. Use the version-matched checkpoint and token dictionary.

## Step 2. Establish the baseline

Extract pretrained cell embeddings and inspect condition, donor, and batch in
both the original space and a visualization. First compare a majority-class
baseline and a linear classifier on frozen embeddings using donor-disjoint
splits. If warranted, compare fine-tuning using the same splits. Select models
and centroids on development donors; evaluate fixed choices on untouched donors.
A fine-tuned model that separates conditions can still reflect batch or donor
shortcuts. Report per-class F1 and per-donor performance, not only cell accuracy.

Keep cell representation settings identical across reference extraction and
perturbation: same checkpoint, layer, embedding mode, tokenizer and code version.
Use cell-type-specific centroids; a mixed PBMC centroid may simply reflect a
change in cell composition. If resting and stimulated reference states overlap
or vary strongly by donor, explain that limitation before ranking genes.

## Step 3. Pilot the perturbation

1. Use the authors' [in silico perturbation notebook](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/in_silico_perturbation.ipynb)
   with your installed version. Filter to eligible stimulated CD8 T cells.
2. Choose `delete` as the illustrative edit. It removes a gene token from the
   ranked input; it does not simulate a particular CRISPR protocol or predict
   expression counts. Define the candidate gene universe before inspecting hits.
3. Use `genes_to_perturb="all"` and `combos=0` for an individual-gene screen,
   or one **single-gene** Ensembl-ID list per run. A list containing several
   genes is interpreted as a combined edit, not separate single-gene tests.
   Check the [API](https://geneformer.readthedocs.io/en/latest/geneformer.in_silico_perturber.html)
   for the pinned version.
4. Pilot a modest, donor-balanced sample; estimate runtime and check output
   files, eligible cells and token detection before expanding. Keep the
   stimulation label and donor identity attached to the results.
5. Compare each edit with appropriate detection- and rank-matched control
   genes. Inspect the shift toward the resting reference and any alternate
   state as well as original-versus-perturbed impact.

For a simple mathematical illustration, if a stimulated cell has cosine
similarity 0.60 to a resting centroid before an edit and 0.64 afterwards,
the shift is +0.04 toward that reference. It does not mean a 4% reduction in
activation. Confirm how the installed version computes and labels its output;
some reported scores may be defined differently.

## Step 4. Summarize and validate

Summarize shifts **within each donor** first, then assess the direction and
magnitude across donors. Provide each gene's number of eligible cells and donors,
median or mean donor-level shift, uncertainty, matched-control comparison and
multiple-testing correction. A result based on one donor or on many cells from
one donor is exploratory. Show a gene-by-donor effect table rather than treating
all cells as independent. If a gene is detected only in activated cells, its
selection may itself bias the comparison.

For stronger evidence, compare prespecified predictions with independent
perturbation data in a compatible cell type, stimulus and time point, including
simple baselines. Follow-up experiments might use gene-targeting guides and
non-targeting controls, measure activation markers and viability, and include
biological replicates. A model shift alone is not evidence of a clinical effect.

## What you should understand

You can explain why a one-donor PBMC demo is not a disease or activation
perturbation study, how donor-disjoint validation works, and how a gene-list
edit becomes a candidate for experimental follow-up.

## Troubleshooting

| Problem | Next check |
| --- | --- |
| No resting/stimulated labels | Obtain an appropriately labeled dataset; do not invent them for PBMC 3k |
| One donor dominates the result | Balance or summarize by donor and report eligible donor counts |
| No shift or tiny gene coverage | Check cell labels, gene ID mapping, detection, reference separation and the exact output definition |
| Out of GPU memory | Reduce forward batch size or pilot cells, then record the revised settings |

Continue to the [cardiomyocyte lesson](perturbation-cardiomyocytes.md) or return
to the [advanced guide](paper-pipeline.md).
