import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  useAutoRunDiscussion,
  useGenerateFeedback,
  useRunNextTurn,
  useSessionRuntimeEvents,
  useSessionStatus,
  useSessionTranscript,
  useSubmitUserTurn
} from "../features/sessions/hooks";
import { useRuntimeReviewList } from "../features/runtimeReviews/hooks";
import { toUserErrorMessage } from "../features/runtimeReviews/mappers";

function turnText(turn: { text?: unknown }) {
  return String(turn.text || "");
}

function turnRole(turn: { speaker_role?: unknown; role?: unknown }) {
  return String(turn.speaker_role || turn.role || "unknown");
}

export default function SessionDetailPage() {
  const { sessionId = "" } = useParams();
  const statusQuery = useSessionStatus(sessionId);
  const submitUserTurn = useSubmitUserTurn(sessionId);
  const runNextTurn = useRunNextTurn(sessionId);
  const autoRun = useAutoRunDiscussion(sessionId);
  const feedback = useGenerateFeedback(sessionId);
  const pendingReviews = useRuntimeReviewList("pending", { sessionId });
  const transcriptQuery = useSessionTranscript(sessionId, 20);
  const [selectedRunId, setSelectedRunId] = useState<string>("");
  const runtimeEventsQuery = useSessionRuntimeEvents(sessionId, selectedRunId || undefined, 20);

  const [userText, setUserText] = useState("");
  const [maxSteps, setMaxSteps] = useState(2);
  const [actionOutput, setActionOutput] = useState<string>("");

  const status = statusQuery.data;
  const busy =
    submitUserTurn.isPending || runNextTurn.isPending || autoRun.isPending || feedback.isPending;

  const errorText = useMemo(() => {
    const err =
      statusQuery.error ||
      submitUserTurn.error ||
      runNextTurn.error ||
      autoRun.error ||
      feedback.error ||
      pendingReviews.error ||
      transcriptQuery.error ||
      runtimeEventsQuery.error;
    return err ? toUserErrorMessage(err) : "";
  }, [
    statusQuery.error,
    submitUserTurn.error,
    runNextTurn.error,
    autoRun.error,
    feedback.error,
    pendingReviews.error,
    transcriptQuery.error,
    runtimeEventsQuery.error
  ]);

  const sessionPendingReviews = pendingReviews.data || [];
  const transcriptTurns = transcriptQuery.data?.pages.flatMap((p) => p.items || []) || [];
  const runtimeEvents = runtimeEventsQuery.data?.pages.flatMap((p) => p.items || []) || [];
  const runIdOptions = Array.from(new Set(runtimeEvents.map((x) => x.run_id).filter(Boolean))) as string[];

  if (statusQuery.isLoading) return <div className="loading">Loading session...</div>;
  if (!status) return <div className="error">Session not found.</div>;

  return (
    <section className="stack">
      <div>
        <Link to="/sessions">Back to sessions</Link>
      </div>
      <header>
        <h2>Session {String(status.session_id)}</h2>
        <p>
          phase={String(status.phase || "-")} | topic={status.topic_id || "-"} | provider={String(status.provider_name || "-")}
        </p>
      </header>

      <div className="grid-two">
        <div className="card">
          <h3>Status</h3>
          <p>runtime_profile_id: {String(status.runtime_profile_id || "-")}</p>
          <p>retrieval_mode: {String(status.retrieval_mode || "-")}</p>
          <p>has_indexes: {String(status.has_indexes)}</p>
          <p>turn_count: {status.turn_count ?? 0}</p>
          <p>peek_next_role: {status.peek_next_role || "-"}</p>
          <p>feedback_ready: {String(status.feedback_ready)}</p>
        </div>
        <div className="card">
          <h3>Linked Runtime Reviews</h3>
          {sessionPendingReviews.length === 0 ? <div className="empty">No pending runtime reviews.</div> : null}
          {sessionPendingReviews.map((r) => (
            <div key={String(r.review_id)}>
              <Link to={`/runtime-reviews/${String(r.review_id)}`}>{String(r.review_id)}</Link> ({String(r.status || "-")})
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>Actions</h3>
        <div className="form-row">
          <textarea
            value={userText}
            onChange={(e) => setUserText(e.target.value)}
            placeholder="Type user turn"
            rows={4}
            disabled={busy}
          />
        </div>
        <div className="actions-row">
          <button
            disabled={busy || userText.trim().length === 0}
            onClick={() =>
              submitUserTurn.mutate(
                { text: userText.trim() },
                { onSuccess: () => setUserText("") }
              )
            }
          >
            Submit User Turn
          </button>
          <button
            disabled={busy}
            onClick={() =>
              runNextTurn.mutate(undefined, {
                onSuccess: (r) =>
                  setActionOutput(`run-next => role=${r.generated_role || "-"} text=${r.generated_reply || "-"}`)
              })
            }
          >
            Run Next Turn
          </button>
          <label>
            max_steps
            <input
              type="number"
              min={1}
              max={8}
              value={maxSteps}
              onChange={(e) => setMaxSteps(Number(e.target.value || "1"))}
            />
          </label>
          <button
            disabled={busy}
            onClick={() =>
              autoRun.mutate(
                { max_steps: maxSteps },
                { onSuccess: (r) => setActionOutput(`auto-run => new_turns=${r.new_turns.length}`) }
              )
            }
          >
            Auto Run
          </button>
          <button
            disabled={busy}
            onClick={() =>
              feedback.mutate(undefined, {
                onSuccess: (r) => setActionOutput(`feedback => ${r.coach_text.slice(0, 120)}`)
              })
            }
          >
            Generate Feedback
          </button>
        </div>
        {actionOutput ? <div className="loading">{actionOutput}</div> : null}
      </div>

      {errorText ? <div className="error">{errorText}</div> : null}

      <div className="card">
        <h3>Transcript (full, paginated)</h3>
        {transcriptQuery.isLoading ? <div className="loading">Loading transcript...</div> : null}
        {transcriptTurns.length === 0 ? <div className="empty">No turns yet.</div> : null}
        <div className="turn-list">
          {transcriptTurns.map((t, idx) => (
            <div className="turn-item" key={`${String(t.turn_id || idx)}`}>
              <div className="turn-meta">
                <strong>{turnRole(t)}</strong>{" "}
                {Boolean((t.metadata as Record<string, unknown> | undefined)?.manual_override || t.manual_override) ? (
                  <span className="pill pill-resumed">manual_override</span>
                ) : null}
                {t.review_id ? (
                  <>
                    {" "}
                    <Link to={`/runtime-reviews/${t.review_id}`}>review:{t.review_id}</Link>
                  </>
                ) : null}
              </div>
              <div className="turn-text">{turnText(t)}</div>
            </div>
          ))}
        </div>
        {transcriptQuery.hasNextPage ? (
          <button disabled={transcriptQuery.isFetchingNextPage} onClick={() => transcriptQuery.fetchNextPage()}>
            {transcriptQuery.isFetchingNextPage ? "Loading..." : "Load More Transcript"}
          </button>
        ) : null}
      </div>

      <div className="card">
        <h3>Runtime Timeline</h3>
        <div className="form-row">
          <label>
            run_id
            <select value={selectedRunId} onChange={(e) => setSelectedRunId(e.target.value)}>
              <option value="">All runs</option>
              {runIdOptions.map((rid) => (
                <option key={rid} value={rid}>
                  {rid}
                </option>
              ))}
            </select>
          </label>
        </div>
        {runtimeEventsQuery.isLoading ? <div className="loading">Loading runtime timeline...</div> : null}
        {runtimeEvents.length === 0 ? <div className="empty">No runtime events found.</div> : null}
        <div className="turn-list">
          {runtimeEvents.map((evt, idx) => (
            <div className="turn-item" key={`${evt.timestamp}-${evt.node_name}-${idx}`}>
              <div className="turn-meta">
                <strong>{evt.node_name}</strong> | {evt.timestamp}
              </div>
              <div>
                run_id={evt.run_id} | stop_reason={evt.stop_reason || "-"} | quality_decision=
                {evt.quality_decision || "-"} | success={String(evt.success)}
              </div>
              <div>
                review_id:{" "}
                {evt.review_id ? <Link to={`/runtime-reviews/${String(evt.review_id)}`}>{String(evt.review_id)}</Link> : "-"}
              </div>
              {evt.error_summary ? <div className="error">{evt.error_summary}</div> : null}
            </div>
          ))}
        </div>
        {runtimeEventsQuery.hasNextPage ? (
          <button
            disabled={runtimeEventsQuery.isFetchingNextPage}
            onClick={() => runtimeEventsQuery.fetchNextPage()}
          >
            {runtimeEventsQuery.isFetchingNextPage ? "Loading..." : "Load More Timeline"}
          </button>
        ) : null}
      </div>

      {status.coach_text_preview ? (
        <div className="card">
          <h3>Feedback Preview</h3>
          <p>{String(status.coach_text_preview)}</p>
        </div>
      ) : null}
    </section>
  );
}
