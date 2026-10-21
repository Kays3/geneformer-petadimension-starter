# Lesson 10. Lessons from real runs

Lessons 1 to 9 get a small example to run. This lesson is for the day you
point Geneformer at a real question and a long GPU job. It collects what went
wrong, and what we would now do first, in a multi-week Geneformer study of
cardiomyocyte and immune-cell states in human tissue, run on shared GPU
machines. Each point is a practice, the reason for it, and a small example.
None of this is specific to one dataset.

## 1. Budget the GPU time before you start

Estimate the cost of a job before you launch it, write the estimate down, and
set a hard cap that the job checks while it runs.

- **Time a small trial first.** Run 5 to 10 cells (or one gene) end to end,
  measure the wall-clock time, and project to the full job. Do this on the
  machine and settings you will really use.
- **Give a low and a high estimate**, and set the cap at the high one. For
  perturbation runs, time grows faster than linearly with cell length, so
  project with the steeper curve, not the flattering one. In our runs the
  measured cost per unit of work for the full job came out between two and
  four times the figure from the small trial, mostly because long cells cost
  much more than short ones.
- **Count GPU-hours as wall-clock hours of a running GPU job**, idle gaps
  included. A job that sits finished for an hour still cost an hour if you
  were not watching. Keep a running total, with the date, host and what it
  paid for.
- **Stop at the cap.** A runner script should read the cap, compare the
  projection after the first unit of work, and stop and report if the
  projection is over it, instead of running to the end and asking afterwards.
- **Look at the job soon after launching it**, not hours later. One short check run
  had finished and its result sat unread for about 91 minutes because nobody
  polled.

## 2. Memory: batch size, headroom, and one job per machine

- **Check free memory before you start** (`free -g`, column `available`).
  Leave at least 15 GB free on a shared machine, whatever the job needs.
  Running a machine to zero stops other people's work as well as yours.
- **One heavy job per machine.** Two large jobs at once usually run slower
  than one after the other, and a memory failure takes both.
- **Size batches to memory, not to speed.** If you see `CUDA out of memory`,
  halve `forward_batch_size` (or the training batch size) and run a short
  trial. Peak memory for the same job on a CPU can be much smaller than on a
  GPU, and the reverse is common for fine-tuning.
- **Some GPU machines share one memory pool between CPU and GPU.** On such
  a machine the memory the GPU holds is memory the rest of the system cannot
  use, and the `nvidia-smi` utilisation percentage is not a reliable sign of
  whether a job is busy. Read the memory column and the process list.
- **Real example:** a one-sequence structure prediction (not Geneformer) for
  a 76-residue protein peaked at 8.4 GB of resident memory on a GPU machine
  that looked idle. Measure the first run with `/usr/bin/time -v` and write
  the number down.

## 3. Check the output after every run

A run that finishes is not a run that worked. After every job, scan the
output for the failures that do not raise an error.

- **Count NaN values, exact zeros, and the spread of the values**, and read
  the median. Treat the output as unusable until you have looked at these
  numbers. The quickstart does this in `check_output` and stops if the output
  is all zero, contains NaN, or is nearly constant.
- **Real example.** One perturbation run wrote 7.8 million values and every
  one was exactly zero. The model had been run in half precision (`bf16`),
  which stores about three significant digits. The quantity measured is a
  cosine similarity between a cell before and after a gene edit, which sits
  very close to 1, so the likely cause is that the difference was rounded
  away. We confirmed that half precision gave zero on every value we tested.
  Repeating the run in full precision (`fp32`) gave tiny non-zero numbers,
  about 1e-7, close to rounding noise. The `fp32` run was
  slower, by a factor between 1.5 and 5 in our measurements, and that cost was
  worth paying for output that carried information. Even then, in one
  full-precision run 102 of 240 summary cells were exactly zero, and we said
  so in the report instead of leaving it out.
- **A control that cannot fail proves nothing.** To check that a no-change
  edit leaves the output unchanged, run two independent forward passes over
  the same input. Re-using the first tensor makes the difference zero by
  construction.
- **Keep a short machine-readable check file next to the output** (counts of
  values, zeros, NaN, the median), and read it before you use the results.
- **Run a tiny end-to-end test first.** Almost every real run in our study found
  something that reading the code and testing on made-up data did not, for
  example a crash on a code path that only runs when every gene in a
  group is ineligible.

## 4. Controls and sample size

- **Compare a gene with matched control genes.** A shift that is small, and
  similar to the shift from random genes of similar expression, is not
  informative. A per-gene reading needs enough control genes: in one analysis
  the method needed 20 control columns, only 7 matched genes were available,
  and the correct answer was "not estimable" for the per-gene adjusted
  reading, not an estimate from 7.
- **The unit of analysis is usually the donor or sample, not the cell.**
  Thousands of cells from three donors are three observations for most
  biological questions. Say what N is in every table and every claim.
- **Check your test by simulation before you trust it.** In a simulation
  with no true effect, a per-gene signed-rank test rejected at least one gene
  in about three quarters of runs, because genes differ by small systematic
  offsets that the test does not model. A set-level test of the same data
  rejected at 4% to 7% against a nominal 5%. A false-positive rate you have
  not measured is not 5%.
- **Small groups get descriptions, not verdicts.** With fewer than about 50
  cells in a group, report the numbers and the direction as observations, with
  their spread, and do not rank or declare a winner.
- **Cross-model comparisons need the unit named.** Results from a 104M and a
  316M model are not the same ranking unit unless you say so, and the
  state-average embeddings from one model size cannot be reused for another
  (their dimensions differ: 768 against 1152).

## 5. Registered and exploratory analyses

- **Write down the test, the threshold and the compute cap before you run.**
  A short dated file in the repository is enough, and so is an issue.
- **Label every result** as registered (decided before seeing the data) or
  exploratory (decided after). Keep both, and put the label in the table
  heading, so it cannot be lost when a figure is copied into slides.
- **If you change a plan, add an amendment instead of editing the plan.**
  State what changed, why, and what had already been run. A calibrated or
  alternative p-value is a sensitivity analysis next to the registered one,
  not a replacement.
- **Name the exact file or column behind every quantity** in a design. A
  phrase such as "median token rank" is ambiguous until you say which table it
  comes from, and the person writing the code cannot guess.

## 6. Environment details that cost us time

- Pin `transformers<5` and `pandas<3` for Geneformer, as the quickstart does.
- Run data-loading with one worker process (`nproc=1`) on GPU jobs if you see
  a crash soon after CUDA starts. Forking after CUDA is initialised can
  crash.
- Record the Geneformer commit, the model name and the library versions with
  every result. Set them from the run, not from memory.
- Large outputs and model files do not belong in Git. Write a hash of each
  input file next to the results.

## You should now see

A short checklist you can apply before and after any real job: budget and
cap, memory headroom, output scan, controls with a stated N, registered or
exploratory label, and recorded versions.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| The job finished but every output value is zero | Half-precision quantisation, or an output path that was never written | Repeat a tiny trial in full precision and compare; do not use the zeros |
| The cap check stops the job after the first unit | The projection is above the cap | Report the projection and ask before raising the cap; do not edit the cap in the script |
| A per-gene result says "not estimable" | Too few control genes for that gene | Report it as not estimable; use a set-level comparison instead |

Previous: [9. Next steps](09-next-steps.md) · Back to the [README](../README.md)
