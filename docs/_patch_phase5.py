from pathlib import Path

from docx import Document

src = Path(r"D:\MSIT\Subjects\AODB\Group Project\AODB_Group3_Phase5.docx")
dst = Path(r"D:\MSIT\Subjects\AODB\Group Project\AODB_Group3_Phase5_ALIGNED.docx")

doc = Document(str(src))

new_intro = (
    "The proposed architecture shall be evaluated through the StreamSphere Proof of Concept. "
    "The PoC shall validate core recommendation workflows, database integration, API communication, "
    "external metadata import, and basic governance controls at reduced scale. "
    "Full TO-BE components such as Kafka streaming, Redis caching, and vector retrieval remain part of "
    "the target architecture and may be validated in later iterations; they are not required for the "
    "initial PoC acceptance. Results shall identify improvements and distinguish proposed targets from "
    "actual measurements."
)

# Update intro paragraph for 7.3.5
for p in doc.paragraphs:
    if p.text.startswith("The proposed architecture shall be evaluated through the StreamSphere Proof of Concept"):
        # Keep existing style by rewriting runs carefully
        if p.runs:
            p.runs[0].text = new_intro
            for run in p.runs[1:]:
                run.text = ""
        else:
            p.text = new_intro
        break

new_rows = [
    ("Evaluation Area", "PoC Validation (Phase 6 scope)"),
    (
        "Transactional Integrity",
        "Verify PostgreSQL ratings, viewing history, and user preference reads/writes.",
    ),
    (
        "Cross-Database Integration",
        "Verify one workflow that uses PostgreSQL + MongoDB joined by movie_id.",
    ),
    (
        "Recommendation Workflow",
        "Validate genre-overlap ranking using PostgreSQL preferences + MongoDB metadata.",
    ),
    (
        "API Integration",
        "Verify REST endpoints used by the UI and documented in OpenAPI (/docs).",
    ),
    (
        "External Integration",
        "Verify TMDB search/import when configured, or documented local fallback.",
    ),
    (
        "Data Quality",
        "Test required fields and reject history/ratings for nonexistent MongoDB movie_id values.",
    ),
    (
        "Security / Governance",
        "Verify login, password hashing, Viewer vs Admin restrictions, and audit logging.",
    ),
    (
        "Performance (basic)",
        "Measure recommendation endpoint elapsed_ms and simple API response times.",
    ),
]

# Locate evaluation table
target = None
for table in doc.tables:
    header = table.rows[0].cells[0].text.strip()
    if header.startswith("Evaluation Area"):
        target = table
        break

if target is None:
    raise SystemExit("Evaluation table not found")

# Ensure row count matches
while len(target.rows) < len(new_rows):
    target.add_row()

# If extra rows exist beyond replacement set, clear them
for idx, (left, right) in enumerate(new_rows):
    row = target.rows[idx]
    row.cells[0].text = left
    row.cells[1].text = right

for idx in range(len(new_rows), len(target.rows)):
    for cell in target.rows[idx].cells:
        cell.text = ""

doc.save(str(dst))
print("wrote", dst)
