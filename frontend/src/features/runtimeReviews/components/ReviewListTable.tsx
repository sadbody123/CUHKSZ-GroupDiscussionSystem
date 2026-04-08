import { Link } from "react-router-dom";

import type { RuntimeReviewSummary } from "../../../api/generated-adapters";
import StatusPill from "../../../components/common/StatusPill";

export default function ReviewListTable({ items }: { items: RuntimeReviewSummary[] }) {
  if (items.length === 0) {
    return <div className="empty">No runtime reviews found for current filter.</div>;
  }
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Review ID</th>
          <th>Status</th>
          <th>Session</th>
          <th>Topic</th>
          <th>Reason</th>
          <th>Actions</th>
          <th>Updated</th>
        </tr>
      </thead>
      <tbody>
        {items.map((r) => (
          <tr key={String(r.review_id)}>
            <td>
              <Link to={`/runtime-reviews/${String(r.review_id)}`}>{String(r.review_id)}</Link>
            </td>
            <td>
              <StatusPill status={r.status || "pending"} />
            </td>
            <td>
              <Link to={`/sessions/${String(r.session_id)}`}>{String(r.session_id)}</Link>
            </td>
            <td>{r.topic_id || "-"}</td>
            <td>{r.interrupt_reason || "-"}</td>
            <td>{(r.allowed_actions || []).join(", ") || "-"}</td>
            <td>{r.updated_at ? new Date(r.updated_at).toLocaleString() : "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
