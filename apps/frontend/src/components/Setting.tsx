import { useEffect, useRef, useState } from "react";

type SettingProps = {
  label: string;
  name: string;
  initial: string;
  onSave: (newValue: string) => void;
};

export function Setting({ label, name, initial, onSave }: SettingProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [value, setValue] = useState(initial);
  const inputRef = useRef<HTMLInputElement>(null);

  const hasChanged = value !== initial;

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
    }
  }, [isEditing]);

  function handleCancel() {
    setValue(initial);
    setIsEditing(false);
  }

  function handleSave() {
    onSave(value);
    setIsEditing(false);
  }

  return (
    <>
      <label htmlFor={name}>{label}</label>

      <input
        ref={inputRef}
        type="text"
        name={name}
        id={name}
        value={value}
        readOnly={!isEditing}
        onChange={(event) => setValue(event.target.value)}
      />

      {isEditing ? (
        <div>
          <button onClick={handleCancel}>Cancel</button>
          <button onClick={handleSave} disabled={!hasChanged}>
            Save changes
          </button>
        </div>
      ) : (
        <button onClick={() => setIsEditing(true)}>Edit</button>
      )}
    </>
  );
}
