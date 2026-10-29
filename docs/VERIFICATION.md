# Verification record

*Documentation by Nakata - Making this study easier to understand.*

Verified on 14 October 2026 against the source files identified in `data/source_manifest.json`.

| Check | Result |
|---|---|
| Source content | All five downloaded files matched the saved SHA-256 hashes. Four Parquet files contain 15,168,579 rows. |
| Data pipeline | Nine recorded checks pass, including source count, zone uniqueness, reconciled exclusions, route/day totals and broad-cohort containment. |
| Analytical unit tests | 11 tests passed. Fixtures cover aggregation, time scenarios, source-month boundaries, daylight-saving exclusions, route joins, retained duplicate signatures, and fare/payment scope. |
| Notebook | Six code cells executed successfully with saved outputs. |
| Dashboard logic | Selecting April gives 2,678,168 comparison trips. At zero added time, displayed rates equal April pooled rates. At 120 airport minutes, airport rates fall while the city comparator stays fixed. |
| Dashboard presentation | Inspected at desktop and phone widths. No whole-page horizontal overflow at the phone breakpoint; wide analytical tables and the hourly plot scroll inside their own regions. |
| PDF | All three rendered pages visually inspected for legibility, clipping, chart labels and source notes. |
| Portable package | ZIP integrity checked. Raw Parquet files, local databases, caches, hosting identity and credentials are excluded. |

The browser checks validate the included controls, not every possible browser or assistive technology. Public source records remain subject to the publisher's accuracy limitations. No operational pilot has been run.
