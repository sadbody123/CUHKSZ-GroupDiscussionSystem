import { useMemo, useState } from "react";

import ReviewMetricsCards from "../features/runtimeReviews/components/ReviewMetricsCards";
import ReviewListTable from "../features/runtimeReviews/components/ReviewListTable";
import { useRuntimeReviewList, useRuntimeReviewMetrics } from "../features/runtimeReviews/hooks";
import { toUserErrorMessage } from "../features/runtimeReviews/mappers";

const statuses = ["pending", "approved", "rejected", "resumed", "resolved"];

export default function RuntimeReviewListPage() {
  const [status, setStatus] = useState("pending");
  const [sessionFilter, setSessionFilter] = useState("");
  const [topicFilter, setTopicFilter] = useState("");
  const listQuery = useRuntimeReviewList(status);
  const metricsQuery = useRuntimeReviewMetrics();

  const error = useMemo(() => {
    if (listQuery.error) return toUserErrorMessage(listQuery.error);
    if (metricsQuery.error) return toUserErrorMessage(metricsQuery.error);
    return "";
  }, [listQuery.error, metricsQuery.error]);

  return (
    <section className="stack">
      <header>
        <h2>Runtime Reviews</h2>
        <p>Inspect interrupted V2 runtime reviews and continue workflow actions.</p>
      </header>

      <div className="filter-row">
        <label htmlFor="status">Status</label>
        <select id="status" value={status} onChange={(e) => setStatus(e.target.value)}>
          {statuses.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <label htmlFor="sessionFilter">Session</label>
        <input
          id="sessionFilter"
          value={sessionFilter}
          onChange={(e) => setSessionFilter(e.target.value)}
          placeholder="filter session_id"
        />
        <label htmlFor="topicFilter">Topic</label>
        <input
          id="topicFilter"
          value={topicFilter}
          onChange={(e) => setTopicFilter(e.target.value)}
          placeholder="filter topic_id"
        />
      </div>

      {metricsQuery.isLoading ? <div className="loading">Loading metrics...</div> : null}
      {metricsQuery.data ? <ReviewMetricsCards metrics={metricsQuery.data} /> : null}

      {error ? <div className="error">{error}</div> : null}
      {listQuery.isLoading ? <div className="loading">Loading reviews...</div> : null}
      {listQuery.data ? (
        <ReviewListTable
          items={listQuery.data.filter((x) => {
            const s = sessionFilter.trim().toLowerCase();
            const t = topicFilter.trim().toLowerCase();
            const passSession = !s || x.session_id.toLowerCase().includes(s);
            const passTopic = !t || String(x.topic_id || "").toLowerCase().includes(t);
            return passSession && passTopic;
          })}
        />
      ) : null}
    </section>
  );
}
