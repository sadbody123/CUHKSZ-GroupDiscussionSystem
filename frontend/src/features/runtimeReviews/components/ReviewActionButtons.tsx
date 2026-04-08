interface Props {
  canApprove: boolean;
  canReject: boolean;
  canResume: boolean;
  canApplyEditedDraft: boolean;
  onApprove: () => void;
  onReject: () => void;
  onResume: () => void;
  onApplyEditedDraft: () => void;
  busy: boolean;
}

export default function ReviewActionButtons(props: Props) {
  return (
    <div className="actions-row">
      <button disabled={!props.canApprove || props.busy} onClick={props.onApprove}>
        Approve
      </button>
      <button disabled={!props.canReject || props.busy} onClick={props.onReject}>
        Reject
      </button>
      <button disabled={!props.canResume || props.busy} onClick={props.onResume}>
        Resume
      </button>
      <button disabled={!props.canApplyEditedDraft || props.busy} onClick={props.onApplyEditedDraft}>
        Apply Edited Draft
      </button>
    </div>
  );
}
