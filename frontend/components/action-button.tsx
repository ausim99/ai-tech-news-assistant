"use client";

import { useState } from "react";

type State = "idle" | "pending" | "success" | "error";

export function ActionButton({
  label,
  pendingLabel,
  onRun,
  variant = "primary",
}: {
  label: string;
  pendingLabel: string;
  onRun: () => Promise<unknown>;
  variant?: "primary" | "secondary";
}) {
  const [state, setState] = useState<State>("idle");
  const [message, setMessage] = useState("");

  async function handleClick() {
    setState("pending");
    setMessage("");
    try {
      await onRun();
      setState("success");
      setMessage("Dispatched - check Workflows for progress.");
    } catch (err) {
      setState("error");
      setMessage(err instanceof Error ? err.message : "Failed to dispatch");
    } finally {
      setTimeout(() => setState("idle"), 4000);
    }
  }

  const base =
    variant === "primary"
      ? "bg-accent text-accent-foreground"
      : "border border-border hover:bg-card";

  return (
    <div className="inline-flex flex-col gap-1">
      <button
        onClick={handleClick}
        disabled={state === "pending"}
        className={`rounded-md px-3 py-1.5 text-sm disabled:opacity-60 transition-colors ${base}`}
      >
        {state === "pending" ? pendingLabel : label}
      </button>
      {message && (
        <span className={`text-xs ${state === "error" ? "text-danger" : "text-success"}`}>{message}</span>
      )}
    </div>
  );
}
