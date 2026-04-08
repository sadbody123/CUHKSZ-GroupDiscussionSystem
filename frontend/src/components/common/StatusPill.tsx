import type { RuntimeReviewStatus } from "../../api/generated-adapters";

const classByStatus: Record<string, string> = {
  pending: "pill pill-pending",
  approved: "pill pill-approved",
  rejected: "pill pill-rejected",
  resumed: "pill pill-resumed",
  resolved: "pill pill-resolved"
};

export default function StatusPill({ status }: { status: RuntimeReviewStatus }) {
  return <span className={classByStatus[String(status)] || "pill"}>{String(status)}</span>;
}
