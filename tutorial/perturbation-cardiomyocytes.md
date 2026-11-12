# Perturbation lesson: cardiomyocytes and cardiomyopathy

This lesson turns the cardiomyopathy application of Geneformer into a guided
learning exercise. Read the [advanced guide](paper-pipeline.md) first. It is
not a runnable reproduction of the paper: the appropriate heart dataset,
metadata, model, splits, and computational environment must be obtained and
verified separately. No outputs or therapeutic targets are claimed here.

## The paper's idea

In the 2023 Geneformer paper, the authors fine-tuned a model to distinguish
cardiomyocyte states from non-failing hearts, hypertrophic cardiomyopathy
(HCM), and dilated cardiomyopathy (DCM). They examined how in silico gene
deletion shifted cell representations between those states and experimentally
followed up selected predictions in engineered cardiac microtissues. See the
[paper and Figure 6](https://pmc.ncbi.nlm.nih.gov/articles/PMC10949956/).
That experimental follow-up supports the specific tested predictions under its
conditions; it does not validate every computational hit.

## Two questions with opposite directions

| Question | Starting cells | Target | Interpretation |
| --- | --- | --- | --- |
| Disease modeling | Non-failing cardiomyocytes | DCM or HCM | Which edits shift the representation toward a disease reference? |
| Candidate rescue | DCM cardiomyocytes | Non-failing | Which edits shift the representation toward a reference state? |

An edit's effect can depend on the starting state. A candidate that moves a
non-failing cell toward DCM is not automatically a target whose deletion
reverses DCM. “Rescue” is a proposed direction in representation space, not
proof that contractility or patient outcomes improve.

## Step 1. Assemble and inspect a suitable dataset

Use human cardiomyocyte data with donor identifiers, phenotype, tissue region,
assay, batch and relevant clinical information. Identify whether the data are
single cells or nuclei, and avoid treating these assay types as interchangeable.
Consider cardiomyocyte subtype, disease cause and severity, medication, age,
sex, and tissue collection: disease labels may align with these factors.
Define the non-failing reference precisely; it is not automatically a perfect
healthy control. Verify raw counts, Ensembl identifiers, gene detection and
V1/V2 tokenizer compatibility, and preserve metadata in the tokenized data.

Split donors before model selection, keeping all cells from each person in one
partition. Compare numbers of donors—not just nuclei—in each condition and
study. Disease confined to a single batch cannot be distinguished reliably
from batch. Use sufficiently independent donors for validation; when numbers
are small, report uncertainty and any missing classes. The original publication's
splits and settings should be obtained from its methods and accompanying code
before describing a run as a replication.

## Step 2. Compare representations and classifiers

Plot pretrained embeddings by phenotype, donor, batch and cell subtype. Use
full-space metrics alongside UMAP. Train a simple frozen-embedding classifier
and, if appropriate, a fine-tuned phenotype classifier with the same
training/validation/test donor splits. Use validation donors to select
hyperparameters and the checkpoint, and assess the final selection on held-out
donors. Report class support, confusion matrix, macro F1 and per-donor results.
Performance on heart tissue does not establish performance on iPSC-derived
cardiomyocytes; these are different biological and technical contexts.

For the perturbation experiment, extract centroids for non-failing, DCM and,
if available, HCM with the same model checkpoint, embedding layer, pooling,
tokenizer and filtering. Construct centroids from development donors for a
held-out evaluation. Document whether centroids are mean or median, check
that no one donor dominates, and quantify their sensitivity to donor sampling.
A centroid is a summary, not a whole disease distribution.

## Step 3. Design a small goal-directed deletion pilot

1. Choose the question and direction in advance. For a candidate-rescue
   exercise, set DCM as start, non-failing as goal, and HCM as an alternate
   state if the data support it. Use the same tissue and cell subtype where
   possible.
2. Follow the authors' [perturbation notebook](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/in_silico_perturbation.ipynb)
   and the [perturber API](https://geneformer.readthedocs.io/en/latest/geneformer.in_silico_perturber.html)
   for your installed revision. With `delete`, each edit removes a gene from
   the input ranks; no physical knockout occurs. `genes_to_perturb="all"` and
   `combos=0` screen individual detected genes. A list of multiple Ensembl IDs
   instead specifies a combined edit; use separate singleton runs for a small
   candidate list.
3. Start with a limited, donor-balanced sample; confirm gene coverage, labels,
   chosen state centroids and output signs before a larger GPU run. Deleting a
   gene can only be evaluated where it is present in the relevant input.
4. Summarize goal-directed shifts within donor and check movement toward the
   alternate state as well. Compare candidates against suitable detection- and
   rank-matched controls; apply appropriate multiple-testing correction and
   disclose the tested gene universe and per-donor coverage.
5. Freeze the selection and test it in held-out donors or an independent
   cohort. Then evaluate selected candidates experimentally with matched
   controls and biological replicates, including functional endpoints appropriate
   to the model, such as contractile force and viability.

Illustration only: a DCM cell's similarity to the non-failing centroid changes
from 0.52 to 0.56 after an edit. The +0.04 change suggests movement toward that
reference under this definition. It does not establish a change in ejection
fraction, gene-expression fold changes or actual contractile rescue. Check the
installed tool's score definition before interpreting its sign.

## Step 4. Decide what the result supports

A useful report states checkpoint and code version, donor splits, phenotype
and reference definitions, perturbation type, gene coverage, number of donors,
per-donor effects, uncertainty, multiple-testing method and matched-control
results. Evaluate competing explanations such as subtype composition and batch.
The most plausible follow-up candidates combine reproducible model shifts with
independent biological evidence and feasible, well-controlled experiments.

## What you should understand

You can distinguish disease modeling from candidate rescue, define a
cardiomyocyte-specific goal, and explain why a shift in a model's embedding
requires independent biological and functional validation.

## Troubleshooting

| Problem | Next check |
| --- | --- |
| Phenotype separates perfectly by study | Check whether study and phenotype are confounded; add suitable data before causal claims |
| Gene absent in many cells | Verify gene ID, vocabulary and detection; report eligible donor and cell counts |
| A large shift has no clear direction | Compare with the goal and alternate centroids, not only the original cell |
| A hit is driven by one donor | Show donor-level results and reproduce in independent donors |

Return to the [peripheral blood lesson](perturbation-peripheral-blood.md) or
[advanced guide](paper-pipeline.md).
