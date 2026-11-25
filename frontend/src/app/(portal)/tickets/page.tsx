"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";

import { getAssets } from "@/lib/assets";
import { getCurrentUser } from "@/lib/auth";
import {
  approveTicket,
  assignTicket,
  createTicket,
  getActiveTechnicians,
  getTicket,
  getTicketAlerts,
  getTickets,
  returnTicket,
  startTicket,
  submitTicket,
  Ticket,
  TicketDetail,
  TicketStatus,
  type Technician,
  type TicketAlert,
  updateTicketWork,
} from "@/lib/tickets";
import type { AssetNode } from "@/types/asset";

const statusLabels: Record<TicketStatus, string> = {
  NEW: "Mới",
  ASSIGNED: "Đã phân công",
  IN_PROGRESS: "Đang xử lý",
  PENDING_APPROVAL: "Chờ duyệt",
  CLOSED: "Đã đóng",
};

function formatDate(value: string): string {
  return new Date(value).toLocaleString("vi-VN");
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Không thể thực hiện thao tác Ticket.";
}

function nodeLabel(node: AssetNode | undefined, id: string): string {
  return node
    ? `${node.code} — ${node.name}`
    : id;
}

function statusLabel(status: string | null): string {
  if (!status) return "";
  return Object.entries(statusLabels).find(([key]) => key === status)?.[1]
    ?? status;
}

export default function TicketsPage() {
  const [role, setRole] = useState("");
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [assets, setAssets] = useState<AssetNode[]>([]);
  const [alerts, setAlerts] = useState<TicketAlert[]>([]);
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [selectedTicketId, setSelectedTicketId] = useState("");
  const [selectedTicket, setSelectedTicket] = useState<TicketDetail | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [nodeId, setNodeId] = useState("");
  const [alertId, setAlertId] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [progress, setProgress] = useState(0);
  const [workNotes, setWorkNotes] = useState("");
  const [evidence, setEvidence] = useState("");
  const [result, setResult] = useState("");
  const [reviewNote, setReviewNote] = useState("");

  const isOperator = role === "Operator";
  const isTechnician = role === "Technician";

  const visibleTickets = useMemo(
    () => tickets.filter(
      (ticket) => !statusFilter || ticket.status === statusFilter,
    ),
    [tickets, statusFilter],
  );

  const matchingAlerts = useMemo(
    () => alerts.filter((alert) => !nodeId || alert.node_id === nodeId),
    [alerts, nodeId],
  );

  async function refreshTickets(signal?: AbortSignal): Promise<Ticket[]> {
    const items = await getTickets(signal);
    if (!signal?.aborted) {
      setTickets(items);
    }
    return items;
  }

  async function openTicket(ticketId: string): Promise<void> {
    setSelectedTicketId(ticketId);
    setSelectedTicket(null);
    const detail = await getTicket(ticketId);
    setSelectedTicket(detail);
    setProgress(detail.progress);
    setWorkNotes(detail.work_notes ?? "");
    setEvidence(detail.evidence ?? "");
    setResult(detail.result ?? "");
    setAssignedTo(detail.assigned_to ?? "");
    setReviewNote("");
    setError("");
  }

useEffect(() => {
  const controller = new AbortController();

  async function loadPage(): Promise<void> {
    try {
      const currentUser = await getCurrentUser();
      if (controller.signal.aborted) return;

      const currentRole = currentUser?.role;
      if (typeof currentRole !== "string") {
        throw new Error("Không xác định được vai trò tài khoản.");
      }
      setRole(currentRole);

      const isCurrentUserOperator = currentRole === "Operator";
      const [ticketItems, assetItems, activeTechnicians, alertItems] =
        await Promise.all([
          getTickets(controller.signal),
          getAssets(controller.signal),
          isCurrentUserOperator
            ? getActiveTechnicians(controller.signal)
            : Promise.resolve<Technician[]>([]),
          isCurrentUserOperator
            ? getTicketAlerts(controller.signal)
            : Promise.resolve<TicketAlert[]>([]),
        ]);

      if (controller.signal.aborted) return;

      setTickets(ticketItems);
      setAssets(assetItems);

      if (isCurrentUserOperator) {
        setTechnicians(activeTechnicians);
        setAlerts(alertItems);

        const query = new URLSearchParams(window.location.search);
        const requestedNodeId = query.get("nodeId") ?? "";
        const requestedAlertId = query.get("alertId") ?? "";

        const requestedAlert = alertItems.find(
          (alert) => alert.id === requestedAlertId,
        );

        if (requestedAlert) {
          setAlertId(requestedAlert.id);
          setNodeId(requestedAlert.node_id);
        } else if (
          requestedNodeId &&
          assetItems.some((asset) => asset.id === requestedNodeId)
        ) {
          setNodeId(requestedNodeId);
        }
      }

      if (ticketItems.length > 0) {
        setSelectedTicketId(ticketItems[0].id);

        const detail = await getTicket(
          ticketItems[0].id,
          controller.signal,
        );

        if (controller.signal.aborted) return;

        setSelectedTicket(detail);
        setProgress(detail.progress);
        setWorkNotes(detail.work_notes ?? "");
        setEvidence(detail.evidence ?? "");
        setResult(detail.result ?? "");
        setAssignedTo(detail.assigned_to ?? "");
      }
    } catch (loadError) {
      if (!controller.signal.aborted) {
        setError(getErrorMessage(loadError));
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }

  void loadPage();

  return () => controller.abort();
}, []);
  async function runTicketAction(
    ticketId: string,
    successMessage: string,
    action: () => Promise<unknown>,
  ): Promise<void> {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      const currentTickets = await refreshTickets();
      if (currentTickets.some((ticket) => ticket.id === ticketId)) {
        await openTicket(ticketId);
      } else {
        setSelectedTicket(null);
        setSelectedTicketId("");
      }
      setNotice(successMessage);
    } catch (actionError) {
      setError(getErrorMessage(actionError));
    } finally {
      setBusy(false);
    }
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const ticket = await createTicket({
        node_id: nodeId,
        ...(alertId ? { alert_id: alertId } : {}),
        title,
        description,
      });
      setTitle("");
      setDescription("");
      setAlertId("");
      await refreshTickets();
      await openTicket(ticket.id);
      setNotice("Đã tạo Ticket.");
    } catch (createError) {
      setError(getErrorMessage(createError));
    } finally {
      setBusy(false);
    }
  }

  function chooseAlert(value: string) {
    setAlertId(value);
    const alert = alerts.find((item) => item.id === value);
    if (alert) {
      setNodeId(alert.node_id);
    }
  }

  const selectedNode = assets.find(
    (asset) => asset.id === selectedTicket?.node_id,
  );

  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Ticket bảo trì
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            {isOperator
              ? "Tạo, phân công và duyệt kết quả Ticket."
              : "Theo dõi và cập nhật các Ticket được giao cho bạn."}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void refreshTickets().catch((refreshError) => {
            setError(getErrorMessage(refreshError));
          })}
          disabled={loading || busy}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white disabled:opacity-50"
        >
          Làm mới
        </button>
      </header>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p role="alert" className="text-sm text-red-800">{error}</p>
        </div>
      )}
      {notice && (
        <p role="status" className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">
          {notice}
        </p>
      )}

      {isOperator && (
        <form
          onSubmit={(event) => void handleCreate(event)}
          className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6"
        >
          <h2 className="text-lg font-semibold text-slate-900">
            Tạo Ticket
          </h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="text-sm font-medium text-slate-700">
              Node
              <select
                required
                value={nodeId}
                onChange={(event) => {
                  setNodeId(event.target.value);
                  setAlertId("");
                }}
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
              >
                <option value="">Chọn Node</option>
                {assets.map((asset) => (
                  <option key={asset.id} value={asset.id}>
                    {asset.code} — {asset.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="text-sm font-medium text-slate-700">
              Cảnh báo liên quan (không bắt buộc)
              <select
                value={alertId}
                onChange={(event) => chooseAlert(event.target.value)}
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
              >
                <option value="">Tạo thủ công, không gắn cảnh báo</option>
                {matchingAlerts.map((alert) => (
                  <option key={alert.id} value={alert.id}>
                    {alert.status} — {alert.message}
                  </option>
                ))}
              </select>
            </label>

            <label className="text-sm font-medium text-slate-700 md:col-span-2">
              Tiêu đề
              <input
                required
                maxLength={200}
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2"
              />
            </label>

            <label className="text-sm font-medium text-slate-700 md:col-span-2">
              Mô tả công việc
              <textarea
                required
                maxLength={4000}
                rows={3}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2"
              />
            </label>
          </div>
          <button
            type="submit"
            disabled={busy || loading || assets.length === 0}
            className="mt-4 rounded-lg bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800 disabled:opacity-50"
          >
            {busy ? "Đang lưu..." : "Tạo Ticket"}
          </button>
        </form>
      )}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
        <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Danh sách Ticket
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                {isTechnician
                  ? "Chỉ hiển thị Ticket được phân công cho bạn."
                  : "Tra cứu toàn bộ Ticket trong hệ thống."}
              </p>
            </div>
            <label className="text-sm text-slate-700">
              Trạng thái
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
                className="ml-2 rounded-lg border border-slate-300 bg-white px-2 py-2"
              >
                <option value="">Tất cả</option>
                {Object.entries(statusLabels).map(([status, label]) => (
                  <option key={status} value={status}>{label}</option>
                ))}
              </select>
            </label>
          </div>

          {loading && (
            <p role="status" className="mt-6 text-sm text-slate-600">
              Đang tải Ticket...
            </p>
          )}
          {!loading && visibleTickets.length === 0 && (
            <p role="status" className="mt-6 rounded-lg bg-slate-50 p-4 text-sm text-slate-600">
              Không có Ticket phù hợp.
            </p>
          )}
          {!loading && visibleTickets.length > 0 && (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[560px] text-left text-sm">
                <thead className="border-b border-slate-200 bg-slate-50 text-slate-700">
                  <tr>
                    <th scope="col" className="px-3 py-3">Tiêu đề</th>
                    <th scope="col" className="px-3 py-3">Trạng thái</th>
                    <th scope="col" className="px-3 py-3">Tiến độ</th>
                    <th scope="col" className="px-3 py-3">Cập nhật</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {visibleTickets.map((ticket) => (
                    <tr
                      key={ticket.id}
                      className={ticket.id === selectedTicketId ? "bg-cyan-50" : "hover:bg-slate-50"}
                    >
                      <th scope="row" className="px-3 py-3 font-medium text-slate-900">
                        <button
                          type="button"
                          onClick={() => void openTicket(ticket.id).catch((openError) => {
                            setError(getErrorMessage(openError));
                          })}
                          className="text-left hover:text-cyan-800"
                        >
                          {ticket.title}
                        </button>
                      </th>
                      <td className="px-3 py-3 text-slate-700">
                        {statusLabels[ticket.status]}
                      </td>
                      <td className="px-3 py-3 text-slate-700">
                        {ticket.progress}%
                      </td>
                      <td className="px-3 py-3 text-slate-600">
                        {formatDate(ticket.updated_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <h2 className="text-lg font-semibold text-slate-900">
            Chi tiết và xử lý
          </h2>
          {!selectedTicket && (
            <p role="status" className="mt-4 text-sm text-slate-600">
              Chọn một Ticket để xem nội dung và thao tác.
            </p>
          )}

          {selectedTicket && (
            <div className="mt-4 space-y-4">
              <div>
                <h3 className="font-semibold text-slate-900">
                  {selectedTicket.title}
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  {selectedTicket.description}
                </p>
                <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
                  <dt className="text-slate-500">Node</dt>
                  <dd className="text-right text-slate-800">
                    {nodeLabel(selectedNode, selectedTicket.node_id)}
                  </dd>
                  <dt className="text-slate-500">Trạng thái</dt>
                  <dd className="text-right text-slate-800">
                    {statusLabels[selectedTicket.status]}
                  </dd>
                  <dt className="text-slate-500">Người được giao</dt>
                  <dd className="text-right text-slate-800">
                    {technicians.find((item) => item.id === selectedTicket.assigned_to)?.email
                      ?? selectedTicket.assigned_to
                      ?? "Chưa phân công"}
                  </dd>
                </dl>
              </div>

              {isOperator && (
                <>
                  {["NEW", "ASSIGNED"].includes(selectedTicket.status) && (
                    <form
                      onSubmit={(event) => {
                        event.preventDefault();
                        void runTicketAction(
                          selectedTicket.id,
                          "Đã phân công Technician.",
                          () => assignTicket(selectedTicket.id, {
                            assigned_to: assignedTo,
                            version: selectedTicket.version,
                          }),
                        );
                      }}
                      className="space-y-3 rounded-lg bg-slate-50 p-3"
                    >
                      <label className="block text-sm font-medium text-slate-700">
                        Phân công Technician đang hoạt động
                        <select
                          required
                          value={assignedTo}
                          onChange={(event) => setAssignedTo(event.target.value)}
                          className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                        >
                          <option value="">Chọn Technician</option>
                          {technicians.map((technician) => (
                            <option key={technician.id} value={technician.id}>
                              {technician.email}
                            </option>
                          ))}
                        </select>
                      </label>
                      <button
                        type="submit"
                        disabled={busy || technicians.length === 0}
                        className="rounded-lg bg-cyan-700 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
                      >
                        Lưu phân công
                      </button>
                    </form>
                  )}

                  {selectedTicket.status === "PENDING_APPROVAL" && (
                    <div className="space-y-3 rounded-lg bg-amber-50 p-3">
                      <p className="text-sm font-semibold text-amber-900">
                        Kết quả: {selectedTicket.result || "Chưa có"}
                      </p>
                      <label className="block text-sm font-medium text-slate-700">
                        Ghi chú duyệt / lý do trả lại
                        <textarea
                          rows={2}
                          value={reviewNote}
                          onChange={(event) => setReviewNote(event.target.value)}
                          className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                        />
                      </label>
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => void runTicketAction(
                            selectedTicket.id,
                            "Đã duyệt đóng Ticket.",
                            () => approveTicket(selectedTicket.id, {
                              version: selectedTicket.version,
                              ...(reviewNote.trim() ? { note: reviewNote.trim() } : {}),
                            }),
                          )}
                          className="rounded-lg bg-emerald-700 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
                        >
                          Duyệt đóng
                        </button>
                        <button
                          type="button"
                          disabled={busy || !reviewNote.trim()}
                          onClick={() => void runTicketAction(
                            selectedTicket.id,
                            "Đã trả Ticket về xử lý.",
                            () => returnTicket(selectedTicket.id, {
                              version: selectedTicket.version,
                              reason: reviewNote.trim(),
                            }),
                          )}
                          className="rounded-lg bg-amber-700 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
                        >
                          Trả lại xử lý
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}

              {isTechnician && selectedTicket.status === "ASSIGNED" && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => void runTicketAction(
                    selectedTicket.id,
                    "Đã bắt đầu xử lý Ticket.",
                    () => startTicket(selectedTicket.id, {
                      version: selectedTicket.version,
                    }),
                  )}
                  className="rounded-lg bg-cyan-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                >
                  Bắt đầu xử lý
                </button>
              )}

              {isTechnician && selectedTicket.status === "IN_PROGRESS" && (
                <div className="space-y-4">
                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void runTicketAction(
                        selectedTicket.id,
                        "Đã cập nhật tiến độ.",
                        () => updateTicketWork(selectedTicket.id, {
                          version: selectedTicket.version,
                          progress,
                          work_notes: workNotes,
                          evidence,
                        }),
                      );
                    }}
                    className="space-y-3 rounded-lg bg-slate-50 p-3"
                  >
                    <label className="block text-sm font-medium text-slate-700">
                      Tiến độ: {progress}%
                      <input
                        type="range"
                        min={0}
                        max={100}
                        value={progress}
                        onChange={(event) => setProgress(Number(event.target.value))}
                        className="mt-2 w-full accent-cyan-700"
                      />
                    </label>
                    <label className="block text-sm font-medium text-slate-700">
                      Nội dung công việc
                      <textarea
                        maxLength={4000}
                        rows={3}
                        value={workNotes}
                        onChange={(event) => setWorkNotes(event.target.value)}
                        className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                      />
                    </label>
                    <label className="block text-sm font-medium text-slate-700">
                      Bằng chứng (văn bản hoặc đường dẫn)
                      <textarea
                        maxLength={4000}
                        rows={2}
                        value={evidence}
                        onChange={(event) => setEvidence(event.target.value)}
                        className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                      />
                    </label>
                    <button
                      type="submit"
                      disabled={busy}
                      className="rounded-lg border border-cyan-700 px-3 py-2 text-sm font-semibold text-cyan-800 disabled:opacity-50"
                    >
                      Lưu tiến độ
                    </button>
                  </form>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void runTicketAction(
                        selectedTicket.id,
                        "Đã gửi kết quả chờ Operator duyệt.",
                        () => submitTicket(selectedTicket.id, {
                          version: selectedTicket.version,
                          result,
                          ...(evidence.trim() ? { evidence } : {}),
                        }),
                      );
                    }}
                    className="space-y-3 rounded-lg border border-cyan-100 p-3"
                  >
                    <label className="block text-sm font-medium text-slate-700">
                      Kết quả xử lý
                      <textarea
                        required
                        maxLength={4000}
                        rows={3}
                        value={result}
                        onChange={(event) => setResult(event.target.value)}
                        className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2"
                      />
                    </label>
                    <button
                      type="submit"
                      disabled={busy || !result.trim()}
                      className="rounded-lg bg-cyan-700 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
                    >
                      Gửi chờ duyệt
                    </button>
                  </form>
                </div>
              )}

              {selectedTicket.status === "PENDING_APPROVAL" && (
                <div className="rounded-lg border border-slate-200 p-3 text-sm text-slate-600">
                  <p>
                    <span className="font-medium">Tiến độ:</span>{" "}
                    {selectedTicket.progress}%
                  </p>
                  {selectedTicket.work_notes && (
                    <p className="mt-2">
                      <span className="font-medium">Ghi chú:</span>{" "}
                      {selectedTicket.work_notes}
                    </p>
                  )}
                  {selectedTicket.evidence && (
                    <p className="mt-2 break-words">
                      <span className="font-medium">Bằng chứng:</span>{" "}
                      {selectedTicket.evidence}
                    </p>
                  )}
                </div>
              )}

              {selectedTicket.result && selectedTicket.status !== "PENDING_APPROVAL" && (
                <p className="rounded-lg border border-slate-200 p-3 text-sm text-slate-700">
                  <span className="font-semibold">Kết quả:</span>{" "}
                  {selectedTicket.result}
                </p>
              )}

              <section>
                <h3 className="text-sm font-semibold text-slate-900">
                  Lịch sử thao tác
                </h3>
                {selectedTicket.history.length === 0 ? (
                  <p className="mt-2 text-sm text-slate-500">Chưa có lịch sử.</p>
                ) : (
                  <ol className="mt-2 max-h-56 space-y-3 overflow-y-auto border-l-2 border-slate-200 pl-4">
                    {selectedTicket.history.map((item) => (
                      <li key={item.id} className="text-sm">
                        <p className="font-medium text-slate-800">
                          {item.action.replaceAll("_", " ")}
                          {item.to_status
                            ? ` · ${statusLabel(item.to_status)}`
                            : ""}
                        </p>
                        <p className="text-xs text-slate-500">
                          {formatDate(item.created_at)} · {item.actor_id}
                        </p>
                        {item.note && (
                          <p className="mt-1 text-slate-600">{item.note}</p>
                        )}
                      </li>
                    ))}
                  </ol>
                )}
              </section>
            </div>
          )}
        </section>
      </div>
    </section>
  );
}
