import { apiFetch } from "@/lib/api-client";

export type TicketStatus =
  | "NEW"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "PENDING_APPROVAL"
  | "CLOSED";

export type TicketHistory = {
  id: string;
  ticket_id: string;
  actor_id: string;
  action: string;
  from_status: string | null;
  to_status: string | null;
  note: string | null;
  details: Record<string, unknown> | null;
  created_at: string;
};

export type Ticket = {
  id: string;
  node_id: string;
  alert_id: string | null;
  created_by: string;
  assigned_to: string | null;
  status: TicketStatus;
  title: string;
  description: string;
  progress: number;
  work_notes: string | null;
  evidence: string | null;
  result: string | null;
  version: number;
  created_at: string;
  updated_at: string;
};

export type TicketDetail = Ticket & {
  history: TicketHistory[];
};

export type Technician = {
  id: string;
  email: string;
};

export type TicketAlert = {
  id: string;
  node_id: string;
  status: string;
  message: string;
};

type VersionInput = {
  version: number;
  note?: string;
};

export function getTickets(signal?: AbortSignal): Promise<Ticket[]> {
  return apiFetch<Ticket[]>("/tickets", { signal });
}

export function getTicket(
  ticketId: string,
  signal?: AbortSignal,
): Promise<TicketDetail> {
  return apiFetch<TicketDetail>(
    `/tickets/${encodeURIComponent(ticketId)}`,
    { signal },
  );
}

export function getActiveTechnicians(
  signal?: AbortSignal,
): Promise<Technician[]> {
  return apiFetch<Technician[]>("/tickets/technicians", { signal });
}

export async function getTicketAlerts(
  signal?: AbortSignal,
): Promise<TicketAlert[]> {
  const result = await apiFetch<{ items: TicketAlert[] }>(
    "/alerts?page_size=100",
    {
      signal,
    },
  );
  return result.items;
}

export function createTicket(input: {
  node_id: string;
  alert_id?: string;
  title: string;
  description: string;
}): Promise<Ticket> {
  return apiFetch<Ticket>("/tickets", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function assignTicket(
  ticketId: string,
  input: { assigned_to: string } & VersionInput,
): Promise<Ticket> {
  return apiFetch<Ticket>(
    `/tickets/${encodeURIComponent(ticketId)}/assign`,
    {
      method: "POST",
      body: JSON.stringify(input),
    },
  );
}

export function startTicket(
  ticketId: string,
  input: VersionInput,
): Promise<Ticket> {
  return apiFetch<Ticket>(
    `/tickets/${encodeURIComponent(ticketId)}/start`,
    {
      method: "POST",
      body: JSON.stringify(input),
    },
  );
}

export function updateTicketWork(
  ticketId: string,
  input: {
    version: number;
    progress: number;
    work_notes: string;
    evidence: string;
  },
): Promise<Ticket> {
  return apiFetch<Ticket>(
    `/tickets/${encodeURIComponent(ticketId)}/work`,
    {
      method: "PATCH",
      body: JSON.stringify(input),
    },
  );
}

export function submitTicket(
  ticketId: string,
  input: {
    version: number;
    result: string;
    evidence?: string;
  },
): Promise<Ticket> {
  return apiFetch<Ticket>(
    `/tickets/${encodeURIComponent(ticketId)}/submit`,
    {
      method: "POST",
      body: JSON.stringify(input),
    },
  );
}

export function approveTicket(
  ticketId: string,
  input: VersionInput,
): Promise<Ticket> {
  return apiFetch<Ticket>(
    `/tickets/${encodeURIComponent(ticketId)}/approve-close`,
    {
      method: "POST",
      body: JSON.stringify(input),
    },
  );
}

export function returnTicket(
  ticketId: string,
  input: { version: number; reason: string },
): Promise<Ticket> {
  return apiFetch<Ticket>(
    `/tickets/${encodeURIComponent(ticketId)}/return`,
    {
      method: "POST",
      body: JSON.stringify(input),
    },
  );
}
