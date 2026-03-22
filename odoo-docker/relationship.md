# UBKT Odoo 15 — Module Data Relationships

---

## 1. Core Model Map

```
res.users ──────────────────────────────────────────────────────┐
  + sign_signature (Image)                                       │
  + sign_stamp (Image)                                           │
  + sign_stamp_send (Image)                                      │
  + user_role (pastor/accountant/treasurer/...)                  │
  + is_approval (Boolean)                                        │
  + data_entry_approval (Boolean)                                │
                                                                 ▼
res.partner ◄──────────── followup.stat.by.partner              │
  + is_foreign                  + partner_id                     │
  + total_this_year             + max_followup_id ──► followup.line
  + total_last_year             + balance                        │
  + meet_this_year          + amount_credit_limit                │
  + payment_responsible_id ─────────────────────────────────────┘
  + latest_followup_level_id ──► followup.line

hr.employee
  + is_foreign
  + working_mode
  + hobby

hr.department
  + is_benefactor
```

---

## 2. Accounting Module Relationships

```
account.fiscal.year
  + date_from / date_to
  + company_id ──► res.company

account.budget.post (Budget Positions)
  + account_ids ──►◄── account.account (Many2many)
  + company_id ──► res.company
       ▲
       │ general_budget_id
       │
crossovered.budget ──► crossovered.budget.lines
  + user_id ──► res.users       + analytic_account_id ──► account.analytic.account
  + date_from / date_to         + general_budget_id ──► account.budget.post
  + state                       + planned_amount / practical_amount
                                + crossovered_budget_id ──► crossovered.budget

account.asset.category
  + account_asset_id ──► account.account
  + account_depreciation_id ──► account.account
  + account_depreciation_expense_id ──► account.account
  + journal_id ──► account.journal
  + company_id ──► res.company
       ▲
       │ asset_category_id
       │
account.move.line ──► account.move
  + followup_line_id ──► followup.line
  + asset_start_date / asset_end_date

product.template
  + asset_category_id ──► account.asset.category
  + deferred_revenue_category_id ──► account.asset.category

account.financial.report (Self-referential tree)
  + parent_id ──► account.financial.report
  + children_ids ◄── account.financial.report
  + account_ids ──►◄── account.account (Many2many)
  + account_type_ids ──►◄── account.account.type

followup.followup
  + company_id ──► res.company
  + followup_line ◄── followup.line
       │
       ▼
followup.line
  + followup_id ──► followup.followup
  + manual_action_responsible_id ──► res.users
  + email_template_id ──► mail.template
```

---

## 3. Payment & Approval Workflow Relationships

```
project.task (Finance Promotion)
  + benefactor ──► hr.employee
  + approval_id ──► res.users
  + land_owner ──► res.partner
  + attachment_id ──►◄── ir.attachment
  + currency_id ──► res.currency
       │
       │ project_task_id
       ▼
account.payment  ◄──────────────────────────────────────────────┐
  + approval_id ──► res.users                                    │
  + accountant_id ──► res.users                                  │
  + treasurer_id ──► res.users                                   │
  + delivered_person ──► res.users                               │
  + received_person ──► res.users                                │
  + benefactor_id ──► hr.employee                                │
  + pay_currency_id ──► res.currency                             │
  + signature (Image) — digital signature captured on approval   │
                                                                 │
recurring.payment ──► recurring.payment.line ───────────────────┘
  + partner_id ──► res.partner    + payment_id ──► account.payment
  + template_id ──► account.recurring.template
  + journal_id ──► account.journal
  + line_ids ◄── recurring.payment.line

account.recurring.template
  + journal_id ──► account.journal
  + recurring_period / recurring_interval
```

---

## 4. Project Task (ICM Form) Relationships

```
project.task (ICM Form)
  + icm_flag (Boolean) — activates ICM form
  + icm_spintend_name/phone/email — superintendent info
  + icm_land_ownership/obtain — land details
  + icm_official_believers/adult/children — congregation stats
  + icm_total_build_cost_vnd / icm_total_build_cost_usd
  + icm_give_effort_vnd/usd — labor contribution
  + icm_donate_materials/cash/land (vnd/usd)
  + icm_exchange_rate
```

---

## 5. Activity & Notification Relationships

```
res.company
  + activity_due_notification (Boolean)
  + ondue_date_notify / before/after notify settings
  + enter_before/after_first/second_notify (days)
       │
       ▼
mail.activity
  + text_note (computed) — notification text
  → triggers email notifications based on due date rules

res.company (Sticky UI settings)
  + enable_form_view_status_bar
  + enable_list_view_status_bar
  + enable_chatter_header_view
  + enable_grouped_kanban_header_view
```

---

## 6. Credit Limit Relationships

```
res.company
  + account_credit_limit (Boolean)
  + account_default_credit_limit (Monetary)
       │
       ▼
res.partner
  + amount_credit_limit (Monetary)
  + credit_limit_compute (computed)
  + show_credit_limit (Boolean)
       │
       ▼
account.move / sale.order
  + partner_credit (related)
  + partner_credit_limit (related)
  + show_partner_credit_warning (computed) — warns if over limit
```

---

## 7. Bank Statement Import

```
account.bank.statement.import (Wizard)
  + attachment_ids ──►◄── ir.attachment (Many2many)
       │
       ▼
account.bank.statement.line
  + unique_import_id — prevents duplicate imports
```

---

## 8. Cross-Module Summary Table

| Model | Extended By | Key Relations |
|---|---|---|
| `res.partner` | contacts_custom, om_account_followup, om_credit_limit | res.users, followup.line, account.move.line |
| `res.users` | contacts_custom | sign images, user_role |
| `res.company` | om_fiscal_year, sh_activity_base, sh_all_in_one_sticky, om_credit_limit | account.fiscal.year |
| `account.move` | om_account_asset, om_credit_limit | account.asset.depreciation.line |
| `account.move.line` | om_account_asset, om_account_followup | account.asset.category, followup.line |
| `account.payment` | account_custom | project.task, res.users (×5), hr.employee |
| `project.task` | project_custom | res.users, hr.employee, res.partner, ir.attachment |
| `product.template` | om_account_asset | account.asset.category (×2) |
| `hr.employee` | employee_custom | — |
| `hr.department` | employee_custom | — |
| `mail.activity` | sh_acitivity_notification | — |
| `sale.order` | om_credit_limit | res.partner (credit) |
