# UBKT Odoo 15 — Step-by-Step Workflow

---

## WORKFLOW 1: Project / Construction Request

### Overview
A church/branch submits a construction or finance project for review and approval through a multi-stage process.

---

### Step-by-Step

```
STEP 1 — CREATE PROJECT TASK
─────────────────────────────────────────────────────
  Who:    Any staff user
  Where:  Project → Tasks → New
  Action: Fill in task details
          Set finance_promotion = True  (for finance projects)
          Set construction_info = True  (for construction projects)
          Set icm_flag = True           (for ICM form projects)

  Auto-assigned:
    approval_id  = Pastor / Authority user (required)
    approved_data_entry = False
    approval_state      = 'open'
    stage               = Data Entry (Stage 1)

──────────────────────────────────────────────────────
STEP 2 — DATA ENTRY
──────────────────────────────────────────────────────
  Who:    Data entry staff
  Action: Fill in all project details:
          • Land info (size, ownership, owner)
          • Church building info (size, materials)
          • Congregation stats (believers count, attendance)
          • Financial info (estimated cost, donations received)
          • ICM fields (superintendent info, language, etc.)

  ⚠ BLOCKED: Cannot move to next stage until Step 3

──────────────────────────────────────────────────────
STEP 3 — APPROVE DATA ENTRY
──────────────────────────────────────────────────────
  Who:    User with data_entry_approval = True
  Where:  Top of task form → Button "Approve Data Entry"
  Action: Click button
  Result: approved_data_entry = True
          → Stage can now be moved forward

──────────────────────────────────────────────────────
STEP 4 — COLLECT OPINIONS
──────────────────────────────────────────────────────
  Who:    Committee / Deacon board / Advisor
  Where:  Task form → "Opinions" tab
  Action: Fill in:
          • opinion_deacon_board (Deacon board opinion)
          • opinion_advisor      (Advisor opinion)

  Stage moves to: STAGE_CONSULT (69) if sending for consultation
               or STAGE_PASTOR  (68) if sending to pastor

──────────────────────────────────────────────────────
STEP 5 — SEND FOR APPROVAL (EMAIL)
──────────────────────────────────────────────────────
  Who:    Staff
  Where:  Task form → Button "Send by Email"
  Action: System selects email template based on stage:
    • Stage = Pastor (68)  → "Project: Send to Approval"
                             → Email sent to approval_id (pastor)
                             → PDF report attached
    • Stage = Consult (69) → "Project: Send consultations"
                             → Email sent to partner_id (church)
                             → Lists all 3 opinions in email body
    • Other stages         → Generic email template

──────────────────────────────────────────────────────
STEP 6 — PORTAL APPROVAL (Pastor/Authority)
──────────────────────────────────────────────────────
  Who:    approval_id user (Pastor)
  Where:  Email link → Portal page
  Action: Review attached PDF report
          Enter opinion in text box
          Click "Accept" OR "Reject"

  ✅ ACCEPT → approval_state = 'approved'
              opinion_pastor = entered message
              Message posted to task chatter

  ❌ REJECT → approval_state = 'rejected'
              opinion_pastor = rejection reason
              Message posted to task chatter
              → Return to Step 4 to revise
```

---

## WORKFLOW 2: Payment / Fund Request

### Overview
A payment request goes through accountant → treasurer → pastor approval before being posted. All three signatures appear on the final receipt.

---

### Step-by-Step

```
STEP 1 — CREATE PAYMENT
──────────────────────────────────────────────────────
  Who:    Finance staff
  Where:  Accounting → Payments → New
  Action: Fill in:
          • Partner (payee)
          • Amount + Currency
          • Exchange rate (if foreign currency)
          • Payment type: Outbound (chi) / Inbound (thu)
          • Journal
          • project_task_id ← REQUIRED for outbound payments
          • Description
          • benefactor_id (hr.employee if advance)

  Auto-assigned from user roles:
    approval_id     = user with role 'pastor' + is_approval=True
    accountant_id   = user with role 'accountant' + is_approval=True
    treasurer_id    = user with role 'treasurer' + is_approval=True
    delivered_person = user with role 'delivered_person'
    received_person  = user with role 'received_person'

  State: DRAFT
  approved_accountant = False
  approved_treasurer  = False

──────────────────────────────────────────────────────
STEP 2 — ACCOUNTANT APPROVAL
──────────────────────────────────────────────────────
  Who:    User with user_role = 'accountant'
  Where:  Payment form → Button "Approved by Accountant"
  Checks: • project_task_id must be filled
            (for outbound, non-advance, non-internal-transfer)
  Result: approved_accountant = True
          State stays DRAFT

──────────────────────────────────────────────────────
STEP 3 — TREASURER APPROVAL
──────────────────────────────────────────────────────
  Who:    User with user_role = 'treasurer'
  Where:  Payment form → Button "Approved by Treasurer"
  Checks: • Same project_task_id check
  Result: approved_treasurer = True
          State stays DRAFT

──────────────────────────────────────────────────────
STEP 4 — SEND TO PASTOR/AUTHORITY FOR APPROVAL
──────────────────────────────────────────────────────
  Who:    Accountant (user_role = 'accountant')
  Where:  Payment form → Button "Send to Approval"
          ⚠ Button only visible when:
            ✓ approved_accountant = True
            ✓ approved_treasurer  = True
            ✓ state = 'draft'
            ✓ current user role = 'accountant'
  Action: Click → mail compose wizard opens
          → Email sent to approval_id (pastor) with PDF attached

  Email:  Subject: "{Company} Payment Receipt (Ref {name_seq})"
          Body:    Payment details + review request
          Attach:  Payment receipt PDF

──────────────────────────────────────────────────────
STEP 5 — PORTAL APPROVAL (Pastor/Authority)
──────────────────────────────────────────────────────
  Who:    approval_id user (Pastor)
  Where:  Email link → Portal page
          URL: /my/account_payments/{id}?access_token=...
  Shows:  • Payment details
          • Amount
          • Project reference
          • Signatures of accountant & treasurer

  ✅ ACCEPT & SIGN
     → System writes:
         signed_by  = approval_id.name
         signed_on  = now()
         signature  = approval_id.sign_signature  ← from user profile
     → action_post() → state = 'POSTED' ✓
     → Confirmation email sent back to approval_id
     → Final PDF has 3 signatures:
         [Pastor signature] [Accountant signature] [Treasurer/Received signature]

  ❌ REJECT
     → action_cancel() → state = 'CANCEL'
     → Message posted: "Payment rejected by {name}: {reason}"
     → Return to Step 1 to revise

──────────────────────────────────────────────────────
STEP 6 — POSTED (COMPLETE)
──────────────────────────────────────────────────────
  State:  POSTED
  Result: • Journal entry recorded in accounting
          • Payment receipt downloadable from portal
          • 3 signature images displayed on PDF:
              Left:   Pastor (approval_id.sign_signature)
              Middle: Accountant (accountant_id.sign_signature)
              Right:  Treasurer or Received person signature
```

---

## SIGNATURE SYSTEM — How It Works

```
NOT DocuSign — signatures are pre-uploaded images pulled at approval time.

Setup (one time, per user):
  Settings → Users → [user] → Upload images:
    sign_signature  ← handwritten signature scan/photo
    sign_stamp      ← official stamp image
    sign_stamp_send ← stamp used on outgoing documents

At approval time:
  When pastor clicks "Accept & Sign" on portal:
    → system reads approval_id.sign_signature
    → stores it on the payment record
    → prints it on the PDF receipt

Result on PDF (3 columns):
  ┌─────────────┬──────────────────┬──────────────────┐
  │   PASTOR    │   ACCOUNTANT     │   TREASURER /    │
  │  signature  │   signature      │ RECEIVED PERSON  │
  │   + stamp   │                  │   signature      │
  └─────────────┴──────────────────┴──────────────────┘
```

---

## ROLE SETUP (Required Before Using Workflows)

Set these on each user in **Settings → Users → [user]**:

| Role | user_role value | is_approval | Responsibilities |
|---|---|---|---|
| Pastor / Director | `pastor` | ✓ True | Final approval on tasks & payments |
| Accountant | `accountant` | ✓ True | 1st approval on payments, sends to approval |
| Treasurer | `treasurer` | ✓ True | 2nd approval on payments |
| Money deliverer | `delivered_person` | optional | Signs on outbound payments |
| Money receiver | `received_person` | optional | Signs on inbound payments |
| Data entry approver | (any) | — | Set `data_entry_approval = True` |

---

## WORKFLOW SUMMARY DIAGRAM

```
PROJECT TASK:
  Create → Data Entry → [Approve Data Entry] → Collect Opinions
        → [Send Email] → Portal Review → Approved ✓ / Rejected ✗

PAYMENT:
  Create (Draft)
    → [Accountant approves]
    → [Treasurer approves]
    → [Send to Approval email]
    → Portal: Pastor signs
    → Posted ✓  /  Cancelled ✗
         ↓
    PDF with 3 signatures generated
```

---

## KEY FILES

| File | Purpose |
|---|---|
| `project_custom/models/construction_info.py` | Task approval states & email |
| `project_custom/models/finance_promotion.py` | Data entry approval & payment link |
| `account_custom/models/account_payment.py` | Payment approval chain |
| `account_custom/controllers/portal.py` | Signature capture on portal |
| `project_custom/controllers/portal.py` | Task accept/reject on portal |
| `account_custom/data/mail_template_data.xml` | Payment email templates |
| `project_custom/data/mail_template_data.xml` | Project email templates |
