# Alert & Maintenance Ticket API Contract

## Conventions

- Protected endpoints require a valid Bearer JWT. The backend derives the actor and role from the authenticated account.
- Request and response bodies use JSON.
- `400` means invalid input, `401` unauthenticated, `403` forbidden, `404` not found, `409` invalid lifecycle transition or stale version, and `503` temporary database failure.

## Ticket lifecycle

`NEW → ASSIGNED → IN_PROGRESS → PENDING_APPROVAL → CLOSED`

An Operator can create and assign a ticket, approve closure, or return it to `IN_PROGRESS` with a required reason. A Technician can start and update only tickets assigned to that account, then submit a non-empty result for approval. A returned ticket retains its assignment and can be updated and submitted again. Closing a ticket does not change or recover its linked Alert.

Every write requires the current positive `version`; a successful update increments it. A mismatch returns `409` without writing either the ticket or its history. Ticket changes and their history/audit event are committed in the same database transaction.

## Endpoints

| Method and path | Access | Purpose |
|---|---|---|
| `GET /tickets?status=...` | Operator; Technician sees assigned tickets only | List tickets; status is optional |
| `POST /tickets` | Operator | Create a manual ticket or link an Alert using `node_id`, optional `alert_id`, `title`, and `description` |
| `GET /tickets/{ticket_id}` | Operator; assigned Technician | Ticket details and change history |
| `GET /tickets/{ticket_id}/history` | Operator; assigned Technician | Ordered audit/history events |
| `POST /tickets/{ticket_id}/assign` | Operator | Assign/reassign an active Technician with `assigned_to` and `version` |
| `POST /tickets/{ticket_id}/start` | Assigned Technician | Start an `ASSIGNED` ticket with `version` |
| `PATCH /tickets/{ticket_id}/work` | Assigned Technician | Update `progress` (0–100), `work_notes`, or text `evidence` with `version` |
| `POST /tickets/{ticket_id}/submit` | Assigned Technician | Submit a required non-empty `result`, optional text `evidence`, and `version` for approval |
| `POST /tickets/{ticket_id}/approve-close` | Operator | Close a `PENDING_APPROVAL` ticket with `version`; a result is mandatory |
| `POST /tickets/{ticket_id}/return` | Operator | Return a `PENDING_APPROVAL` ticket with `version` and a required `reason` |

Evidence is captured as text or a reference in JSON; this API does not accept or store uploaded files. No file type, size, or download-access policy is implied.

## Ticket history

History records the actor, timestamp, action, previous/next state, note, and structured field details where applicable. Create, assign, start, work updates, submission, approval, and return are recorded in the same transaction as the ticket mutation.

An `alert_id` must exist and its `node_id` must match the ticket's `node_id`.
