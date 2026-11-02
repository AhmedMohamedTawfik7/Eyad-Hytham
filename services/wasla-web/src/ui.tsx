import { createContext, useContext } from "react";
import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
  InputHTMLAttributes,
  MouseEvent,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  appearance?: "primary" | "secondary" | "subtle";
  size?: "large";
};

export function Button({
  appearance = "secondary",
  size,
  type = "button",
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      type={type}
      className={`ui-button ${appearance}${size ? ` ${size}` : ""} ${className}`.trim()}
    />
  );
}

export function Card({
  className = "",
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return <div {...props} className={`ui-card ${className}`.trim()} />;
}

type FieldProps = {
  label: ReactNode;
  required?: boolean;
  hint?: ReactNode;
  children: ReactNode;
};

export function Field({ label, required, hint, children }: FieldProps) {
  return (
    <label className="ui-field">
      <span className="ui-label">
        {label}{required && <span aria-hidden="true"> *</span>}
      </span>
      {children}
      {hint && <span className="ui-hint">{hint}</span>}
    </label>
  );
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`ui-input ${props.className ?? ""}`.trim()} />;
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={`ui-select ${props.className ?? ""}`.trim()} />;
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`ui-textarea ${props.className ?? ""}`.trim()} />;
}

export function Spinner({ label, size }: { label?: string; size?: "tiny" }) {
  return (
    <span className={`ui-spinner${size ? ` ${size}` : ""}`} role="status" aria-label={label}>
      <span aria-hidden="true" />
      {label && <span className="ui-spinner-label">{label}</span>}
    </span>
  );
}

type TabsState = {
  selectedValue: string;
  onSelect: (
    event: MouseEvent<HTMLButtonElement>,
    data: { value: string },
  ) => void;
};

const TabsContext = createContext<TabsState | null>(null);

export function TabList({
  selectedValue,
  onTabSelect,
  children,
}: {
  selectedValue: string;
  onTabSelect: TabsState["onSelect"];
  children: ReactNode;
}) {
  return (
    <TabsContext.Provider value={{ selectedValue, onSelect: onTabSelect }}>
      <div className="ui-tablist" role="group">{children}</div>
    </TabsContext.Provider>
  );
}

export function Tab({ value, children }: { value: string; children: ReactNode }) {
  const tabs = useContext(TabsContext);
  if (!tabs) throw new Error("Tabs must be rendered inside a tab list.");
  return (
    <button
      type="button"
      aria-pressed={tabs.selectedValue === value}
      className="ui-tab"
      onClick={(event) => tabs.onSelect(event, { value })}
    >
      {children}
    </button>
  );
}
