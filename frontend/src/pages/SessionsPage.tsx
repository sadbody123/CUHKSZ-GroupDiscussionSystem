import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useCreateSession, useProfiles, useSessionList, useSnapshots, useTopics } from "../features/sessions/hooks";
import { toUserErrorMessage } from "../features/runtimeReviews/mappers";

export default function SessionsPage() {
  const navigate = useNavigate();
  const sessionsQuery = useSessionList();
  const snapshotsQuery = useSnapshots();
  const profilesQuery = useProfiles();
  const createMutation = useCreateSession();

  const [snapshotId, setSnapshotId] = useState("");
  const [topicId, setTopicId] = useState("");
  const [providerName, setProviderName] = useState("mock");
  const [runtimeProfileId, setRuntimeProfileId] = useState("default");
  const [userStance, setUserStance] = useState("");

  const topicsQuery = useTopics(snapshotId);

  const errorText = useMemo(() => {
    const err =
      sessionsQuery.error ||
      snapshotsQuery.error ||
      profilesQuery.error ||
      topicsQuery.error ||
      createMutation.error;
    return err ? toUserErrorMessage(err) : "";
  }, [
    sessionsQuery.error,
    snapshotsQuery.error,
    profilesQuery.error,
    topicsQuery.error,
    createMutation.error
  ]);

  return (
    <section className="stack">
      <header>
        <h2>Discussion Console</h2>
        <p>Create sessions and jump into transcript operations.</p>
      </header>

      <div className="card">
        <h3>Create Session</h3>
        <div className="form-row">
          <label>
            Snapshot
            <select
              value={snapshotId}
              onChange={(e) => {
                setSnapshotId(e.target.value);
                setTopicId("");
              }}
            >
              <option value="">Select snapshot</option>
              {(snapshotsQuery.data || []).map((s) => (
                <option key={String(s.snapshot_id)} value={String(s.snapshot_id)}>
                  {String(s.snapshot_id)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Topic
            <select value={topicId} onChange={(e) => setTopicId(e.target.value)} disabled={!snapshotId}>
              <option value="">Select topic</option>
              {(topicsQuery.data || []).map((t) => (
                <option key={String(t.topic_id)} value={String(t.topic_id)}>
                  {String(t.topic_id)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Provider
            <input value={providerName} onChange={(e) => setProviderName(e.target.value)} />
          </label>
          <label>
            Runtime Profile
            <select value={runtimeProfileId} onChange={(e) => setRuntimeProfileId(e.target.value)}>
              {(profilesQuery.data || []).map((p) => (
                <option key={String(p.profile_id)} value={String(p.profile_id)}>
                  {String(p.profile_id)}
                </option>
              ))}
            </select>
          </label>
          <label>
            User Stance
            <input value={userStance} onChange={(e) => setUserStance(e.target.value)} placeholder="for / against" />
          </label>
          <button
            disabled={!snapshotId || !topicId || createMutation.isPending}
            onClick={() =>
              createMutation.mutate(
                {
                  snapshot_id: snapshotId,
                  topic_id: topicId,
                  provider_name: providerName,
                  runtime_profile_id: runtimeProfileId,
                  user_stance: userStance || undefined
                },
                {
                  onSuccess: (r) => navigate(`/sessions/${r.session_id}`)
                }
              )
            }
          >
            Create Session
          </button>
        </div>
      </div>

      {errorText ? <div className="error">{errorText}</div> : null}
      <div className="card">
        <h3>Sessions</h3>
        {sessionsQuery.isLoading ? <div className="loading">Loading sessions...</div> : null}
        {!sessionsQuery.isLoading && (sessionsQuery.data || []).length === 0 ? (
          <div className="empty">No sessions found.</div>
        ) : null}
        <table className="table">
          <thead>
            <tr>
              <th>Session</th>
              <th>Topic</th>
              <th>Phase</th>
              <th>Turns</th>
              <th>Provider</th>
            </tr>
          </thead>
          <tbody>
            {(sessionsQuery.data || []).map((s) => (
              <tr key={String(s.session_id)}>
                <td>
                  <Link to={`/sessions/${String(s.session_id)}`}>{String(s.session_id)}</Link>
                </td>
                <td>{s.topic_id || "-"}</td>
                <td>{s.phase}</td>
                <td>{s.turn_count ?? 0}</td>
                <td>{String(s.provider_name || "-")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
