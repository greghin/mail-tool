# Mail Inbox Tool

A simple workflow for processing scanned mail. You drop PDFs from the SmartScan app on your phone into `Unsorted/`, and Claude (in Cowork) processes them — extracts text, identifies sender/date/document type, proposes a clean filename and destination folder, and (after you approve) files them away.

## Folder layout

```
Mail Inbox/
├── Unsorted/            ← drop new scans here
├── Checks/              ← payment instruments received
├── Invoices/            ← bills and statements
├── State Documents/     ← government correspondence, licenses, tax notices
├── Other/               ← anything that doesn't fit
└── _mail-tool/
    ├── extract_mail.py  ← OCR + text extraction script
    └── README.md        ← this file
```

## Naming convention

`YYYY-MM-DD - Sender - Subject.pdf`

The date is the document date (issue, billing, or notice date), not the scan date. Sorts chronologically and is scannable by eye.

## How to run

### On a schedule
A weekly scheduled task runs every Thursday at 9pm local time. If Cowork is closed when it's due, it runs on next launch.

### On demand
Open Cowork and say "process my mail" — Claude will pick up whatever is in `Unsorted/` and walk you through it.

## What happens during a run

1. Claude scans `Unsorted/` for PDFs.
2. For each PDF, runs `extract_mail.py` to pull text (direct text layer first, OCR fallback for image-only scans).
3. Reads the text and classifies each one — sender, date, document type, destination folder.
4. Presents a review queue with proposed names and destinations.
5. You approve (or edit), and Claude moves the files.

The review step is intentional — until categorization is reliable, nothing moves without your sign-off.

## Adding new categories

If you start receiving mail that doesn't fit the existing folders (e.g. Tax, Insurance, Legal), just create the subfolder inside `Mail Inbox/`. The next run will see it and consider it as a destination.
