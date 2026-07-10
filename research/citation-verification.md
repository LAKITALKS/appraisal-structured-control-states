# Citation Verification Log

This file records the verification status of every work considered for the
bibliography of this repository. It is the single source of truth for what may
appear in `paper/references.bib`.

**Rule:** A work may enter the formal bibliography only after it has been checked
against a primary source (arXiv, ACL Anthology, NeurIPS, ICLR/OpenReview, an
official publisher page, or the authors' own primary write-up). Anything that
could not be verified in the current pass is listed under **Unverified** and is
deliberately excluded from `references.bib` until a human reviewer confirms it.

Verification pass date: 2026-07-10.
Method: web search restricted to primary-source domains (arxiv.org,
aclanthology.org, proceedings.neurips.cc, openreview.net) plus retrieval of
arXiv abstract pages for exact author lists.

---

## Verified (included in `references.bib`)

| Key | Title | Primary identifier | Venue / status |
| --- | --- | --- | --- |
| `zou2023repe` | Representation Engineering: A Top-Down Approach to AI Transparency | arXiv:2310.01405 | Preprint |
| `turner2023actadd` | Steering Language Models With Activation Engineering | arXiv:2308.10248 | Preprint |
| `arditi2024refusal` | Refusal in Language Models Is Mediated by a Single Direction | arXiv:2406.11717 | NeurIPS 2024 |
| `lee2024cast` | Programming Refusal with Conditional Activation Steering | arXiv:2409.05907 | ICLR 2025 |
| `teplica2025sciurus` | SCIURus: Shared Circuits for Interpretable Uncertainty Representations in Language Models | aclanthology:2025.naacl-long.618 | NAACL 2025 |
| `tak2025emotioninfer` | Mechanistic Interpretability of Emotion Inference in Large Language Models | arXiv:2502.05489 | Findings of ACL 2025 |
| `li2025taskrepr` | Just-in-time and distributed task representations in language models | arXiv:2509.04466 | Preprint |
| `nguyen2025evalaware` | Probing and Steering Evaluation Awareness of Language Models | arXiv:2507.01786 | Preprint |
| `hua2025evaldeployed` | Steering Evaluation-Aware Language Models to Act Like They Are Deployed | arXiv:2510.20487 | Preprint |
| `han2025safeswitch` | SafeSwitch: Steering Unsafe LLM Behavior via Internal Activation Signals | arXiv:2502.01042 | Preprint |
| `sofroniew2026emotion` | Emotion Concepts and their Function in a Large Language Model | arXiv:2604.07729 | Preprint |
| `joad2026morerefusal` | There Is More to Refusal in Large Language Models than a Single Direction | arXiv:2602.02132 | Preprint |
| `lavi2025unanswerability` | Detecting (Un)answerability in Large Language Models with Linear Directions | arXiv:2509.22449 | EACL 2026 |
| `sun2026valencearousal` | Valence-Arousal Subspace in LLMs: Circular Emotion Geometry and Multi-Behavioral Control | arXiv:2604.03147 | Preprint |
| `mack2024melbo` | Mechanistically Eliciting Latent Behaviors in Language Models | AI Alignment Forum (authors' primary write-up) | Technical report |

Notes on individual entries:

- `arditi2024refusal`: an arXiv preprint that also appears in the NeurIPS 2024
  proceedings; both identifiers were confirmed. Author list confirmed from the
  arXiv abstract page.
- `nguyen2025evalaware`: the canonical title on arXiv:2507.01786 is *"Probing and
  Steering Evaluation Awareness of Language Models"*. An earlier version circulated
  under the shorter title *"Probing Evaluation Awareness of Language Models"*; the
  arXiv record is used as the primary identifier.
- `han2025safeswitch`: circulated under the title *"Internal Activation as the
  Polar Star for Steering Unsafe LLM Behavior"*; the arXiv record 2502.01042 now
  carries the title *"SafeSwitch: Steering Unsafe LLM Behavior via Internal
  Activation Signals"*. Same work; the arXiv title is used.
- `sofroniew2026emotion`: an industry research preprint (Anthropic). Cited only as
  a scholarly reference; the citation confers no authorship or endorsement on this
  repository.
- `mack2024melbo`: no arXiv record was located; the authors' own Alignment Forum
  write-up is treated as the primary source and cited as a technical report.

---

## Unverified (excluded from `references.bib` pending human review)

- **"Verbalizable Representations Form a Global Workspace in Language Models."**
  Status: UNVERIFIED. A primary-source record (arXiv / OpenReview / ACL) could not
  be located in the 2026-07-10 verification pass. The concept (a
  workspace-like, privileged, verbalizable representation) is discussed in the
  paper and preregistration in general terms without attributing it to this
  specific unverified title. It must not enter `references.bib` until a reviewer
  confirms a primary identifier.

---

## Reviewer checklist before first release

1. Re-confirm every arXiv identifier resolves and matches the title above.
2. Replace preprint entries with their proceedings versions where a peer-reviewed
   version now exists.
3. Resolve or drop the unverified workspace reference.
4. Add DOIs where publishers assign them.
