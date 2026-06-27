---
name: expense-report
description: Scans a designated OneDrive folder for transaction files (Excel, CSV, PDF, PNG, JPG, and other image receipts), extracts payment data, categorizes each transaction into one of five expense codes using AI judgment, and appends the results to the master expense report Excel file in OneDrive. Use when someone says "run the expense report", "categorize transactions", "process receipts", "update the expense tracker", or any similar request to process pending payments.
---

# Expense Report Skill

When this skill triggers, your job is to scan a OneDrive folder for unprocessed transaction files, extract the payment data from each one, assign an expense category, and write the results into the master expense report Excel file in OneDrive.

---

## Configuration

Update these values to match your environment:

| Setting | Value |
|---|---|
| **OneDrive source folder** | `Receipts` — browse to the root, open `Receipts`, then navigate into the current month's subfolder (e.g. `May 2026`) |
| **Master report file** | Search OneDrive for the current month's report (e.g. `May Expense Report.xlsx`) |
| **Master report sheet** | `Sheet1` (or `Transaction Report` if the sheet was renamed) |
| **Account split (default)** | Your default chart-of-accounts code (update to match your accounting system) |

---

## Expense Category Codes

Assign every transaction to exactly one of the following five codes. Use the descriptions to guide your judgment. When unsure, pick the closest match and note your reasoning in the Notes field.

| Code | Label | What belongs here |
|---|---|---|
| `6080` | Office & Operating Expenses | Supplies, kitchen items, snacks, cleaning, utilities, small equipment, event materials, meals |
| `6100` | Professional Services | Contractors, consultants, freelancers, memberships, subscriptions to professional tools |
| `6200` | Marketing & Events | Event costs, promotional materials, advertising, sponsorships, content production |
| `6300` | Technology & Software | SaaS subscriptions, software licenses, AI tools, hosting, digital infrastructure |
| `6400` | Facilities & Infrastructure | Rent, security, building systems, physical infrastructure, maintenance |

> **Note:** These are example codes. Replace with your organization's actual chart-of-accounts codes.

---

## Workflow

### Step 1 — Find the source folder

1. Use `mcp__ms365__list-drives` to get the user's OneDrive drive ID.
2. Use `mcp__ms365__get-drive-root-item` to get the root folder ID.
3. Use `mcp__ms365__list-folder-files` on the root to find the `Receipts` folder.
4. Once found, list its children to find the current month's subfolder (e.g. `May 2026`).
5. List the files inside that subfolder — these are the receipts to process.

If no `Receipts` folder is found, stop and ask the user to confirm the folder name before proceeding.

### Step 2 — List files in the folder

From the month subfolder, collect each file's `name`, `id`, and file extension.

- Skip subfolders unless the user explicitly asks to recurse.
- If the folder is empty, report: "No files found — nothing to process."
- Supported file types: `.xlsx`, `.xls`, `.csv`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`

### Step 3 — Extract transaction data from each file

Process each file according to its type. For each file, extract these fields:

| Field | Description |
|---|---|
| `Date` | Transaction or invoice date (MM/DD/YYYY) |
| `Transaction Type` | `Expenditure` for payments/purchases, `Deposit` for credits/refunds |
| `Name` | Vendor or payee name (clean, human-readable) |
| `Memo/Description` | The raw description, memo, or line items from the receipt |
| `Amount` | Dollar amount (positive number, no $ sign) |
| `Source File` | The filename — kept for audit trail |

---

**For Excel files (.xlsx, .xls):**
1. Use `mcp__ms365__get-excel-used-range` on the file to read all cell data.
2. Map columns to the fields above — headers may vary, use judgment.
3. Extract each data row as a separate transaction record.

---

**For CSV files (.csv):**
1. Use `mcp__ms365__download-bytes` to download the file content.
2. Parse the CSV in the workspace using Python:
   ```python
   import pandas as pd, io, base64
   raw = base64.b64decode(content_bytes)
   df = pd.read_csv(io.BytesIO(raw))
   ```
3. Map columns to the fields above.

---

**For PDF files (.pdf):**
1. Use `mcp__ms365__download-bytes` to download the file content.
2. Decode the base64 and save to `/tmp/receipt.pdf` in bash:
   ```bash
   python3 -c "import base64; open('/tmp/receipt.pdf','wb').write(base64.b64decode('BASE64_HERE'))"
   ```
3. Extract text using pdfplumber:
   ```python
   import pdfplumber
   with pdfplumber.open('/tmp/receipt.pdf') as pdf:
       text = '\n'.join(page.extract_text() for page in pdf.pages)
   print(text)
   ```
4. Parse the text to identify vendor name, date, total, and line items.
5. If the PDF is a bank statement with multiple transactions, extract each row separately.

---

**For image files (.png, .jpg, .jpeg, .webp, .gif, .bmp) — Claude Vision:**

> This is the preferred approach for photo receipts. Claude reads the image directly — no external OCR service needed.

1. Use `mcp__ms365__get-drive-item` on the file with `select=id,name,@microsoft.graph.downloadUrl` to get a temporary direct download URL.
2. Use bash to download the image into the workspace outputs directory:
   ```bash
   curl -s -L "DOWNLOAD_URL_HERE" -o /PATH/TO/OUTPUTS/receipt_filename.png
   ```
   Use the bash sandbox outputs path from your current session context (visible in your system prompt as the bash mount path for `outputs`).
3. Use the `Read` tool on the corresponding Mac-side outputs path to view the image. Claude will see it natively as a multimodal image.
4. From what you see in the image, extract:
   - **Vendor/merchant name** — usually prominent at the top
   - **Date** — look for a date near the top or bottom
   - **Total amount** — look for "Total", "Amount Due", "Grand Total", or the largest bolded dollar figure
   - **Line items** — individual purchases for the Memo/Description field
   - **Payment method** — card type and last 4 digits if visible
5. If the image is too blurry, cropped, or unreadable, flag it as `NEEDS REVIEW` and continue.

**Tips for reading receipts visually:**
- The "Total" is almost always at the bottom, after tax and tip
- Vendor name is typically the largest text at the top
- If two totals exist (subtotal vs. total), always use the final total paid
- Card receipts often show Auth Code or Transaction ID — include these in the Memo/Description

---

**If a file cannot be read or parsed**, log it as:
`[filename] — Could not extract data. Manual review required.`
Then continue to the next file.

---

### Step 4 — Categorize each transaction

For each transaction record, assign it to one of the five expense codes from the Configuration table.

**Categorization rules:**
- Read the `Name` (vendor) and `Memo/Description` together.
- Apply the category definitions above.
- **Vendor shortcuts** (common examples — update to match your vendors):
  - Amazon → `6080` if memo mentions supplies, snacks, kitchen, batteries, cables; `6300` if software/service
  - Anthropic → `6300` Technology & Software
  - Content tools (podcast hosts, video editors, similar) → `6200` Marketing & Events
  - Restaurants / cafes → `6080` Office & Operating Expenses - Meals & Hospitality

**Build the Notes field** using this format:
```
[Code] [Label] - [Subcategory] - [Specific description]
```
Example: `6080 Office & Operating Expenses - Meals & Hospitality - Staff breakfast at Blue Sail Cafe`

If you cannot confidently categorize, set Notes to:
```
NEEDS REVIEW - [best guess and why you're uncertain]
```

### Step 5 — Find the master report file

1. Use `mcp__ms365__list-folder-files` on the drive root to find the current month's expense report file (e.g. `May Expense Report.xlsx`).
2. Use `mcp__ms365__list-excel-worksheets` to confirm the worksheet ID.
3. Use `mcp__ms365__get-excel-used-range` to read existing rows.
4. Note the last populated row number — new entries will be appended below it.
5. **Duplicate check**: if a transaction with the same Date + Name + Amount already exists, skip it and count it as a duplicate.

### Step 6 — Append new rows to the master report

For each new transaction (not a duplicate), append a row using `mcp__ms365__update-excel-range`.

Target the next empty row's address (e.g. `A4:G4` if row 3 is the last populated row).

Each row must follow this column order exactly:
```
[Date] | [Transaction Type] | [Name] | [Memo/Description] | [Split] | [Amount] | [Notes]
```

- `Split`: always `1050 Cash in Bank - Bank of Tampa 5688 (Program)` unless the source specifies otherwise
- `Date`: MM/DD/YYYY string format
- `Amount`: numeric value only, no currency symbols

### Step 7 — Report back to the user

After all files are processed, produce this summary:

---

**Expense Report — Run Complete**
*[today's date]*

**Processed:** [N] files from `Receipts/[Month Year]/`
**New transactions added:** [N] rows to `[Month] Expense Report.xlsx`
**Duplicates skipped:** [N]

**Transactions by Category:**
- 6080 Office & Operating Expenses: [N] transactions, $[total]
- 6100 Professional Services: [N] transactions, $[total]
- 6200 Marketing & Events: [N] transactions, $[total]
- 6300 Technology & Software: [N] transactions, $[total]
- 6400 Facilities & Infrastructure: [N] transactions, $[total]
- NEEDS REVIEW: [N] transactions

**Items Flagged for Review:**
[List any transactions marked NEEDS REVIEW with a brief note]

---

## Error Handling

| Situation | Action |
|---|---|
| OneDrive folder not found | Stop, ask user to confirm folder name |
| Master report file not found | Stop, ask user to confirm file name |
| File download fails | Log it, skip, continue |
| PDF text extraction returns empty | Flag as manual review, continue |
| Image is unreadable / too blurry | Flag as manual review, continue |
| Duplicate detected | Skip silently, count in summary |
| All files already processed | Report: "All transactions already exist — nothing new to add." |

## Edge Cases

- **Multiple transactions in one file** (bank statement): Extract and process each row individually.
- **Refunds or credits**: Set Transaction Type to `Deposit`.
- **Partial data** (no date visible): Use today's date and flag with `NEEDS REVIEW`.
- **Image receipt with multiple pages**: Download all pages and read each one.
- **Files with no recognizable transaction data**: Skip and add to the manual review list.

## Future Upgrade: Azure AI Document Intelligence

When this skill is migrated to a managed agent (headless, no Claude visual context), replace the Claude Vision image step with Azure AI Document Intelligence:

```python
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

client = DocumentIntelligenceClient(
    endpoint="https://YOUR_RESOURCE.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("YOUR_API_KEY")
)
with open("receipt.png", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-receipt", f)
result = poller.result()

for receipt in result.documents:
    vendor = receipt.fields.get("MerchantName").value
    date   = receipt.fields.get("TransactionDate").value
    total  = receipt.fields.get("Total").value
```

Requires: Azure subscription + Document Intelligence resource. Returns fully structured receipt fields with high accuracy across crumpled, angled, or low-light photos.
