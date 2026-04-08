import type { RuntimeReviewMetrics } from "../../../api/generated-adapters";

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

export default function ReviewMetricsCards({ metrics }: { metrics: RuntimeReviewMetrics }) {
  return (
    <section className="metrics-grid">
      <Card label="Pending" value={metrics.pending_review_count} />
      <Card label="Created" value={metrics.created_review_count} />
      <Card label="Resolved" value={metrics.resolved_review_count} />
      <Card label="Interrupt Rate" value={metrics.interrupt_rate.toFixed(2)} />
      <Card label="Repair Rate" value={metrics.repair_rate.toFixed(2)} />
      <Card label="Manual Overrides" value={metrics.manual_override_count} />
    </section>
  );
}
