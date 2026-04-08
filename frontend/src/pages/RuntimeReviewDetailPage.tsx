import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import ReviewActionButtons from "../features/runtimeReviews/components/ReviewActionButtons";
import {
  useApplyEditedDraft,
  useApproveRuntimeReview,
  useRejectRuntimeReview,
  useResumeRuntimeReview,
  useRuntimeReviewDetail
} from "../features/runtimeReviews/hooks";
import { toUserErrorMessage } from "../features/runtimeReviews/mappers";
import StatusPill from "../components/common/StatusPill";

export default function RuntimeReviewDetailPage() {
  const { reviewId = "" } = useParams();
  const detailQuery = useRuntimeReviewDetail(reviewId);
  const approve = useApproveRuntimeReview(reviewId);
  const reject = useRejectRuntimeReview(reviewId);
  const resume = useResumeRuntimeReview(reviewId);
  const applyEditedDraft = useApplyEditedDraft(reviewId);

  const [editedText, setEditedText] = useState("");
  const [updatedBy, setUpdatedBy] = useState("review_console");
  const [note, setNote] = useState("");
  const [resumeAfterApply, setResumeAfterApply] = useState(false);

  const detail = detailQuery.data;
  const busy = approve.isPending || reject.isPending || resume.isPending || applyEditedDraft.isPending;
  const can = (action: string) => Boolean(detail?.allowed_actions?.includes(action));

  const errorText = useMemo(() => {
    const err = detailQuery.error || approve.error || reject.error || resume.error || applyEditedDraft.error;
    return err ? toUserErrorMessage(err) : "";
  }, [detailQuery.error, approve.error, reject.error, resume.error, applyEditedDraft.error]);

  if (detailQuery.isLoading) return <div className="loading">Loading review detail...</div>;
  if (!detail) return <div className="error">Review not found.</div>;

  const textValue = editedText || detail.draft_reply_text || detail.draft_reply_summary || "";

  return (
    <section className="stack">
      <div>
        <Link to="/runtime-reviews">Back to list</Link>
      </div>
              {detail.session_id ? (
                <div>
                  <Link to={`/sessions/${detail.session_id}`}>Open related session</Link>
                </div>
              ) : null}
      <header className="detail-header">
        <h2>{String(detail.review_id)}</h2>
        <StatusPill status={detail.status || "pending"} />
      </header>

      <div className="grid-two">
        <div className="card">
          <h3>Runtime Context</h3>
          <p>session_id: {String(detail.session_id || "-")}</p>
          <p>run_id: {String(detail.run_id || "-")}</p>
          <p>checkpoint_id: {detail.checkpoint_id || "-"}</p>
          <p>topic_id: {detail.topic_id || "-"}</p>
          <p>version: {detail.version ?? "-"}</p>
        </div>
        <div className="card">
          <h3>Quality Context</h3>
          <p>interrupt_reason: {detail.interrupt_reason || "-"}</p>
          <p>reason: {detail.reason || "-"}</p>
          <p>quality_flags: {(detail.quality_flags || []).join(", ") || "-"}</p>
          <p>policy_id: {String(detail.metadata?.policy_id || "-")}</p>
        </div>
      </div>

      <div className="card">
        <h3>Editable Draft</h3>
        <textarea
          data-testid="edited-draft-input"
          value={textValue}
          onChange={(e) => setEditedText(e.target.value)}
          rows={8}
          disabled={busy || !can("apply_edited_draft")}
        />
        <div className="form-row">
          <label>
            Updated by
            <input value={updatedBy} onChange={(e) => setUpdatedBy(e.target.value)} />
          </label>
          <label>
            Note
            <input value={note} onChange={(e) => setNote(e.target.value)} />
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={resumeAfterApply}
              onChange={(e) => setResumeAfterApply(e.target.checked)}
            />
            Resume after apply
          </label>
        </div>
      </div>

      {errorText ? <div className="error">{errorText}</div> : null}

      <ReviewActionButtons
        canApprove={can("approve")}
        canReject={can("reject")}
        canResume={can("resume")}
        canApplyEditedDraft={can("apply_edited_draft") && textValue.trim().length > 0}
        busy={busy}
        onApprove={() =>
          approve.mutate({
            action: "approve",
            expected_version: detail.version ?? 1,
            updated_by: updatedBy,
            payload: { note }
          })
        }
        onReject={() =>
          reject.mutate({
            reason: note || "Rejected in review console",
            expected_version: detail.version ?? 1,
            updated_by: updatedBy
          })
        }
        onResume={() => resume.mutate({ additional_steps: 1 })}
        onApplyEditedDraft={() =>
          applyEditedDraft.mutate({
            edited_text: textValue,
            expected_version: detail.version ?? 1,
            updated_by: updatedBy,
            note,
            resume_after_apply: resumeAfterApply,
            additional_steps: 1
          })
        }
      />
    </section>
  );
}
