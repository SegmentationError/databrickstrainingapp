import { useEffect, useState } from "react";

type CheckState = "checking" | "ok" | "fail";

function useCheck(path: string): [CheckState, any] {
  const [state, setState] = useState<CheckState>("checking");
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch(path)
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((d) => {
        setData(d);
        setState("ok");
      })
      .catch(() => setState("fail"));
  }, [path]);

  return [state, data];
}

function StatusRow({ label, state, detail }: { label: string; state: CheckState; detail?: string }) {
  const color = state === "ok" ? "#1D7A55" : state === "fail" ? "#B23A2E" : "#888";
  const text = state === "checking" ? "Checking..." : state === "ok" ? "Connected" : "Failed";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0", borderBottom: "1px solid #eee" }}>
      <span style={{ width: 10, height: 10, borderRadius: "50%", background: color, display: "inline-block" }} />
      <span style={{ fontWeight: 500, minWidth: 200 }}>{label}</span>
      <span style={{ color }}>{text}</span>
      {detail && <span style={{ color: "#666", fontSize: 13 }}>— {detail}</span>}
    </div>
  );
}

export default function App() {
  const [whoamiState, whoamiData] = useCheck("/api/whoami");
  const [warehouseState] = useCheck("/api/health/warehouse");
  const [metadataState] = useCheck("/api/health/metadata-store");

  return (
    <div style={{ fontFamily: "system-ui", maxWidth: 640, margin: "60px auto", padding: "0 20px" }}>
      <h1 style={{ color: "#0D009D" }}>Delta Update Portal</h1>
      <p style={{ color: "#666" }}>Scaffolding check — proving the three connectivity paths before any feature logic.</p>

      <StatusRow
        label="Entra ID identity (via Databricks SSO)"
        state={whoamiState}
        detail={whoamiData ? whoamiData.email : undefined}
      />
      <StatusRow label="SQL Warehouse (app service principal)" state={warehouseState} />
      <StatusRow label="Metadata store (Lakebase)" state={metadataState} />
    </div>
  );
}
