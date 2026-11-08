type SettingActionProps = {
  title: string;
  description: string;
  actionLabel: string;
  onAction: () => void;
  actionDisabled?: boolean;
  pendingLabel?: string;
  variant?: "default" | "danger";
};

export function SettingAction({
  title,
  description,
  actionLabel,
  onAction,
  actionDisabled = false,
  pendingLabel,
  variant = "default",
}: SettingActionProps) {
  return (
    <div>
      <h2>{title}</h2>
      <p>{description}</p>
      <button type="button" onClick={onAction} disabled={actionDisabled} data-variant={variant}>
        {actionDisabled && pendingLabel ? pendingLabel : actionLabel}
      </button>
    </div>
  );
}
