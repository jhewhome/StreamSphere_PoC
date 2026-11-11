# Phase 5 Review + PoC Alignment (Options B & C)

Source draft: `AODB_Group3_Phase5.docx` (not yet submitted)  
Guidelines mapping: **Phase 5 = Data Governance + Diagrams**; **Phase 6 = PoC**

## Overall verdict

The draft is already strong for Phase 5. It covers Part 6 (governance) and Part 7 (trade-offs), includes **4 embedded figures**, cites privacy/security/database sources, and stays consistent with StreamSphere’s Phase 4 polyglot story.

It is **close to submittable**, with a few alignment and polish fixes before Classroom upload.

## Rubric / outline coverage

| Required area | Status in draft | Notes |
|---|---|---|
| 6.1 Data Quality | Present | Standards + monitoring metrics are clear |
| 6.2 Data Security | Present | Classification + RBAC + Figure 5.1 |
| 6.3 Privacy & Compliance | Present | DPA primary; GDPR scoped; HIPAA correctly marked N/A |
| 6.4 Lifecycle | Present | Ingestion/storage/archival covered |
| 6.5 Lineage & Auditing | Present | Fits PoC audit-log demo |
| 7.1 DB selection trade-offs | Present | Matches Phase 4 engines |
| 7.2 Architectural trade-offs | Present | CAP/consistency table is useful |
| 7.3 Mitigations | Present | Good operational controls |
| Diagrams | 4 images embedded | Keep labels Figure 5.1–5.4 readable in PDF export |
| References | 10 sources | Enough for this phase; keep final-report total ≥ 8 |

## Critical alignment fix (Phase 5 ↔ PoC)

Section **7.3.5 Continuous Architecture Evaluation** currently says the PoC will validate:

- Kafka event processing
- Vector Database fault tolerance / fallback

Your approved PoC plan and the built prototype intentionally **exclude** Kafka, Redis, and vector search from the first PoC.

### Replace the 7.3.5 evaluation table with this version

| Evaluation Area | PoC Validation (Phase 6 scope) |
|---|---|
| Transactional integrity | Verify PostgreSQL ratings, viewing history, and user preference reads/writes |
| Cross-database integration | Verify one workflow that uses PostgreSQL + MongoDB joined by `movie_id` |
| Recommendation workflow | Validate genre-overlap ranking using PG preferences + Mongo metadata |
| API integration | Verify REST endpoints used by the UI and documented in OpenAPI (`/docs`) |
| External integration | Verify TMDB search/import when API key is configured (or documented local fallback) |
| Data quality | Test required fields and reject ratings/history for nonexistent MongoDB `movie_id` |
| Security / governance | Verify login, password hashing, Viewer vs Admin restrictions, audit logging |
| Performance (basic) | Measure recommendation endpoint `elapsed_ms` and simple API response times |

### Add one clarifying sentence before the table

> The StreamSphere Proof of Concept validates the core polyglot, API, external-integration, and governance controls at reduced scale. Full TO-BE components such as Kafka streaming, Redis caching, and vector retrieval remain part of the target architecture and may be validated in later iterations; they are not required for the initial PoC acceptance.

This keeps Phase 5 honest: full architecture on paper, reduced-scope PoC in practice — which the guidelines explicitly allow.

## Other fixes before submit

1. **Title spacing / cover polish**  
   Export shows glued text (`PHASE 5DATA GOVERNANCE`, `STREAMSPHEREAn AI-Powered...`). Check Word styles/line breaks on the cover before PDF export.

2. **Figure captions**  
   Confirm each figure has a visible caption in the PDF:
   - Figure 5.1 Governance/Security Architecture
   - Figure 5.2 (lifecycle/lineage — verify label)
   - Figure 5.3 (as labeled in your refined diagrams file)
   - Figure 5.4 Architectural Trade-off Model

3. **PoC wording consistency**  
   Search the draft for absolute claims like “the PoC shall verify event propagation through Kafka” and rewrite to “target architecture / future validation” unless you expand PoC scope.

4. **Academic integrity**  
   Guidelines require originality checks on the **final** report. For Phase 5, still:
   - keep citations
   - rewrite any heavily AI-polished paragraphs in your group’s voice
   - do not paste long AI-generated blocks unchanged into the final compilation

5. **Submission naming**  
   `AODB_Group3_Phase5_LastName_FirstName.pdf` for each member.

## How Phase 5 supports the built PoC

| Phase 5 control | PoC evidence |
|---|---|
| Cross-store consistency via shared content IDs | `movie_id` joins PG history/ratings to Mongo movies |
| RBAC / least privilege | Viewer vs Admin routes; admin-only audit/import |
| Password protection | `password_hash` with bcrypt |
| Audit trail | `audit_logs` table + admin UI |
| Retention/privacy awareness | Fictional sample users; no real personal data |
| Trade-off: cost vs capability | PoC uses only PostgreSQL + MongoDB subset |

## Recommended submit order

1. Apply the 7.3.5 alignment edit above
2. Fix cover spacing + figure captions
3. Export PDF and spot-check tables/figures
4. Submit Phase 5
5. Run PoC with Docker and collect Phase 6 evidence using `DEMO_EVIDENCE_CHECKLIST.md`
