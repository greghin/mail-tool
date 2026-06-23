# Setting up the Mail Organizer on a new computer

The mail organizer's folder structure and extraction script live in OneDrive at `Business Operations/Mail Inbox/` and follow you automatically. Only two things need to be re-established on a new machine:

1. **Folder access** — Cowork needs permission to read/write that folder on the new device.
2. **The scheduled task** — stored locally per-machine, not in OneDrive, so the Thursday 9pm schedule must be recreated.

---

## Option A — Install the skill (easiest for team members)

1. Download `process-mail-inbox.skill` from the GitHub repo.
2. In Cowork, go to **Settings → Capabilities** and drag the `.skill` file in, or use the install button that appears when you open the file.
3. Once installed, say **"process my mail"** — Cowork will open a folder picker; select your `Mail Inbox` folder and the workflow runs.

This option does **not** set up the automatic Thursday schedule — use Option B for that.

---

## Option B — Full setup with weekly schedule

Paste the prompt below into a fresh Cowork conversation on the new computer. Adjust the path if your OneDrive sync location differs.

---

### Setup prompt (copy everything between the lines)

---

I'm setting up my mail organizer on a new computer. The folder already exists in OneDrive at:
    /Users/gregor.hintler/Library/CloudStorage/OneDrive-TheMobilityHouse/USA/Business Operations/Mail Inbox
(If that path doesn't exist on this machine, find where OneDrive synced the `Business Operations/Mail Inbox` folder and use the actual path instead.)
Please do the following:
1. Request access to that Mail Inbox folder using `mcp__cowork__request_cowork_directory`.
2. Verify the folder structure is intact. It should contain subfolders `Unsorted`, `Checks`, `Invoices`, `State Documents`, `Other`, and `_mail-tool/`. The `_mail-tool/` folder should contain `extract_mail.py` and `README.md`. If anything is missing, tell me.
3. Create a weekly scheduled task with these exact properties:
   - taskId: `weekly-mail-processing`
   - description: `Weekly: process scanned mail from the Unsorted folder and prepare a review queue`
   - cronExpression: `0 21 * * 4` (every Thursday at 9pm local time)
   - notifyOnCompletion: true
   - prompt: (use the prompt body below verbatim)
   Prompt body for the scheduled task:
   ```
   Process my weekly scanned mail. The Mail Inbox lives at:
       /Users/gregor.hintler/Library/CloudStorage/OneDrive-TheMobilityHouse/USA/Business Operations/Mail Inbox
   Step 1 — Connect the folder. Call `mcp__cowork__request_cowork_directory` with that exact path so you have read/write access.
   Step 2 — Check for new mail. List `Unsorted/` inside that folder. If it's empty (ignoring `.DS_Store`), just report "No new mail to process this week" and stop.
   Step 3 — Extract text. Run the bundled extraction script via `mcp__workspace__bash`. The folder is mounted under `/sessions/<session>/mnt/Mail Inbox` — find the actual mount with `ls /sessions/*/mnt/` if needed, then:
       python3 "<mount>/_mail-tool/extract_mail.py" "<mount>/Unsorted" /tmp/manifest.json
   Step 4 — Classify each item. Read /tmp/manifest.json. For each item, identify from the extracted text:
   - The document date (issue/billing/notice date) → YYYY-MM-DD
   - The sender (institution or company)
   - A short subject (document type + key detail like check number or amount)
   - The destination subfolder, choosing from: `State Documents`, `Checks`, `Invoices`, `Other`. If something genuinely doesn't fit, propose `Other`. If the user has added new subfolders, include those as valid destinations.
   Naming pattern: `YYYY-MM-DD - Sender - Subject.pdf`
   Step 5 — Present the review queue. Show a table to the user with rows: current filename → proposed name → destination. Flag anything ambiguous or low-confidence. Ask for approval (use the AskUserQuestion tool with options like "Approve all" / "Approve with edits" / "Hold").
   Step 6 — After approval, move files using Python via bash. Don't move anything that wasn't explicitly approved. Report what was moved.
   Notes:
   - The categories are case-sensitive on disk: "State Documents", "Checks", "Invoices", "Other".
   - Mail is in English; OCR is already configured for `-l eng`.
   - If the script isn't present (e.g. the user deleted `_mail-tool/`), re-create it from this conversation's history or skip extraction and ask the user how to proceed.
   - Don't auto-create new top-level category folders; ask first if you think one is needed.
   ```
4. After the schedule is created, recommend I click "Run now" once to pre-approve the tool permissions the task will need (folder access, bash), so future Thursday runs don't pause on permission prompts. If `Unsorted/` is empty, the task will just exit cleanly — that's a fine pre-approval pass.
5. Confirm when everything is wired up.

---

## What lives where (for reference)

| Where | What |
|---|---|
| OneDrive (`Mail Inbox/_mail-tool/`) | `extract_mail.py`, `README.md`, this setup file |
| OneDrive (`Mail Inbox/Unsorted/`, `Checks/`, etc.) | The mail itself, organized |
| Local: `~/Claude/Scheduled/weekly-mail-processing/` | The scheduled task definition (needs recreation per-machine) |
| Local: Cowork folder permissions | Granted per-machine, must be re-requested |
| GitHub repo | `extract_mail.py`, `README.md`, `SETUP_ON_NEW_COMPUTER.md`, `process-mail-inbox.skill` |
