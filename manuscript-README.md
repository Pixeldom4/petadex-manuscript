# PETadex manuscript: outstanding gaps

Status of `petadex-manuscript.tex` as of 2026-10-02, after the first round of responses was applied. Resolved items have been removed; what is left still needs an answer, a decision or work. IDs are unchanged from the first version, so gaps in the numbering are items that are done.

Answer in [Responses](#responses) at the bottom, by ID.

**Resolved in round 1 and removed:** A4 (Statistics subsection drafted), D1 (HMM counts), D3 (PAZy retrieval date), D4 (the 15 domains), F8 (unclassified BioSamples), and the answered parts of C1, D5, E1, E2, E4, E5, E6, E7, F1, F7, I1.

## A. Missing sections

| ID | Outstanding | On record |
|---|---|---|
| A1 | Abstract is empty. | |
| A2 | Discussion is one paragraph on the web resource. | An outline of the metadata and HMM points is now a source comment under `\section{Discussion}`. Nothing on record for the dataset as a whole, the case study or general limitations. |
| A3 | Back matter is empty: Supplementary information, Acknowledgements, all eight Declarations items. | Code repositories are noted in a comment next to "Code availability". |
| A5 | No `\section{Figures}`; legends are inline. | |

## B. Citations

| ID | Outstanding | On record |
|---|---|---|
| B1 | `petadex-references.bib` is empty and the text has no `\cite` commands. | The v1 bibliography is in this repo at `archive/v1-petadex-manuscript/petadex-references.bib` (PAZy, PlasticDB, DIAMOND, ESM-2). |
| B2 | Introduction: plastic production and waste, animal biomass, micro- and nanoplastic toxicity, Yoshida 2016, PAZy, Danso 2018, Erickson 2022, Logan, PETadex v1. | |
| B3 | Tool citations. Versions are now in the text; the references are not. | Added to the list since round 1: MMseqs2, InterProScan, UMAP, Mol*, FastTree. JackHMMER is cited as a comparison only. |
| B4 | Cut190, TfCut2, PET30, PET27, PlasticDB, PMBD, and the mechanism papers behind the catalytic-residue annotations. | |

## C. Missing results (v260701 Logan stage)

| ID | Outstanding | On record |
|---|---|---|
| C1 | Five of six Logan values are still `x`: Logan version, hits, nr-matched, clustered, final count. Also the dataset size in the Introduction. | Query size (2.74 million) is filled in. No v260701 Logan search output exists; the query goes to Rayan to run. |
| C2 | The Results heading still says 215.7 million. | The vault carries both 215.7 M and 216.7 M for the v1 figure; check against the Logan paper. |
| C3 | Taxonomy is not computed for v260701; the nr total and percentage are `x`. | Total to use: 7,561,905. Only v1 nr taxonomy exists (5,593,336 rows). |
| C4 | Regenerate the Logan, clustering and metadata numbers (Fig. 3 included) on v260701. | Confirmed v1. Waits on C1. |
| C5 | Worked example of one domain is not written. | Candidate: nr sequence 1JFR_A (NR223), component C001; details in a NOTE comment in Results. |

## D. Numbers that conflict

| ID | Outstanding | On record |
|---|---|---|
| D1a | Results says 7,562,397 HMM hits among nr sequences, but 492 of those are plasticome sequences. Say which number is meant. | 7,561,905 are nr. New item, raised by the D1 answer. |
| D2 | Search benchmark must be redone on the Next.js rebuild. | Current site: 32 shards, ~44 s, DIAMOND v2.2.2. No record of "20 shards, ~47 s". |
| D5 | Say which sequence set the 64,730 Atlas families come from. | They are 60% family representatives (1,046,402 members), not the corpus-wide 60% level (1,814,296 clusters). |

## E. Methods with no record

| ID | Outstanding | On record |
|---|---|---|
| E1 | Logan search: DIAMOND mode and cut-offs, number of accessions, ORF caller and minimum length. | Query construction is now written. Search side: Rayan. |
| E2 | Commands and coverage thresholds for the 90 / 60 / 30% corpus clustering; how folds were assigned to superfamilies. | Logan-query clustering is now written. The v1 clustering inputs are no longer on disk. |
| E3 | Taxonomy: mapping source for nr, handling of sequences with accessions from several taxa, source of run-level taxonomy for Logan. | No response yet. |
| E4 | ESMFold2 recycle count. Which model folded the 22,235 centroids, and at which clustering level. | The other large folding run used ESM3-open; stored ESMFold2 structures are labelled 60%. |
| E5 | SRA / BioSample retrieval date. | The public mirror carries no version. nr and BacDive dates are now in the text. |
| E6 | Web platform for the rebuild: stack, compute, result storage, search sensitivity and cut-offs, ranking, benchmark design, UMAP parameters, kinetics curation protocol. | Current-site values are recorded inside the todos as reference. |
| E7 | Two choices in the case study (see F4a, F4b). | Settings are now written. |

## F. Open decisions

| ID | Decision | On record |
|---|---|---|
| F1 | Run the >90% overlap check, or drop it. Keep or remove the C006-1 profile, which is built from two sequences. | The counting rule is now in Methods. Overlap check has no output. For Thomas. |
| F2 | Inferred temperature: recompute on the 8 September BacDive pull, or hold temperature out. | Standing recommendation is to hold it out. Recompute code is written but not run. pH is unaffected. |
| F3 | Cap BioSamples per BioProject and category, or not. | Capping strengthens the host-heavy vs environment-diverse conclusion slightly. |
| F4 | Case study thesis; ORF-level or cluster-level novelty; whether the T9SS lineage stays in the main text. | Dennis + Artem. Gap is 17.1 points at ORF level and 5.8 at cluster level. |
| F4a | Report cluster-level medians with or without a coverage filter. | No filter: 56.5 / 62.3%. Coverage ≥ 50%: 57.2 / 63.3%. |
| F4b | consenTRAIT permutations: the text says 1,000, the scripts say 999. | |
| F5 | Report the AFragmenter check or leave it out. | Thomas calls it a rough gauge; one known artefact (C014). |
| F6 | Does PlasticESM belong in this paper? | Its licence line is also unconfirmed. |
| F7 | Mean absolute error for temperature against a constant. | pH values are now in Methods. No temperature values recorded. |

## G. Figures

| ID | Outstanding | On record |
|---|---|---|
| G1 | Fig. 1A label should read "recycled or incinerated". | |
| G2 | Fig. 1 PNG is 18898×14173 px; downsample to 600 DPI. | |
| G3 | Swap Fig. 4 to composite v2 and its caption. | v2 is on the server at `~/superfamily-case-study/results/review_20260928/composite_v2/`; not yet copied into `figures/`. Still to fix on v2: TfCut2 / Cut190 label overlap, journal-size export. |
| G4 | Taxonomy panel: supplementary figure, or drop the reference. | |

## H. Supplementary material

`supplementary-figures/` and `tables/` are still empty.

| ID | Item | On record |
|---|---|---|
| H1 | Table: PAZy curation (26 removed, 4 added; handling of indirect-evidence enzymes). | |
| H2 | Table: accession, snapshot and sequence provenance of all 609 enzymes. | |
| H3 | Table: the 13 seed enzymes. | |
| H4 | Table: catalytic residue annotation. Needs formatting and a source-publication column. | `s3/3_msa_cleaning/plasticome.v2.sequence_annotations.csv` (57 rows). Sources are only in the Google Sheet. |
| H5 | Table: per-iteration HMM statistics. Needs formatting. | Three `summary.csv` files in Thomas's tree; paths are in the checklist comment in the `.tex`. |
| H6 | Case-study tables: per-family enrichment, architecture, T9SS families. | Data in `~/superfamily-case-study/results/`. |
| H7 | Figure: search latency against corpus size or query length. | |
| H8 | Data: environment-category rule set. Needs exporting. | `~/sra-proxy-data/pipelines/profiles/scripts/profile_rules.py`. |

## I. Availability and sustainability

| ID | Outstanding | On record |
|---|---|---|
| I1 | Data licence. Confirm the S3 buckets now named in Results are public and final. | Licence is not recorded anywhere. |
| I2 | Code availability statement. | Repositories noted in a comment in Declarations. |
| I3 | Maintenance plan, funding horizon, running cost. | |
| I4 | Confirm the website labels every non-plasticome entry as putative. | |

## J. Prose to rewrite

| ID | Outstanding |
|---|---|
| J1 | AI-drafted blocks: website and case-study Results, the Discussion paragraph, all twelve Methods subsections (Statistics added in round 1). `grep -n "AI-GENERATED" petadex-manuscript.tex`. |
| J2 | The first two paragraphs of Results are single sentences. |

## Housekeeping

- The vault notes `Thomas/Artifact Index.md` and `Thomas/HMM_Documentation.md` still carry the stale 2026-09-04 HMM counts.
- Notebook 5's header gives two finish dates (2026-09-13 and September 26th).
- The nr snapshot can no longer be re-derived from the shared BLAST database; Thomas's FASTA dump and DIAMOND database are the only copies.

---

## Responses

Write under each ID: the answer, who owns it, or "defer". Leave blank if untouched.

### A. Missing sections
- A1:
- A2:
- A3:
- A5:

### B. Citations
- B1:
- B2:
- B3:
- B4:

### C. Missing results
- C1:
- C2:
- C3:
- C4:
- C5:

### D. Numbers that conflict
- D1a:
- D2:
- D5:

### E. Methods with no record
- E1:
- E2:
- E3:
- E4:
- E5:
- E6:

### F. Open decisions
- F1:
- F2:
- F3:
- F4:
- F4a:
- F4b:
- F5:
- F6:
- F7:

### G. Figures
- G1:
- G2:
- G3:
- G4:

### H. Supplementary material
- H1:
- H2:
- H3:
- H4:
- H5:
- H6:
- H7:
- H8:

### I. Availability and sustainability
- I1:
- I2:
- I3:
- I4:

### J. Prose to rewrite
- J1:
- J2:

### Anything else
