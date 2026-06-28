"use client";

import { useEffect, useState } from "react";
import {
  createOwnedMedia,
  deleteOwnedMedia,
  listOwnedMedia,
  type MediaType,
  type OwnedMedia,
} from "@/lib/api";

const MEDIA_TYPES: MediaType[] = ["web", "instagram", "blog", "facebook"];

export function OwnedMediaRegistry({ brandId }: { brandId: number }) {
  const [items, setItems] = useState<OwnedMedia[]>([]);
  const [mediaType, setMediaType] = useState<MediaType>("web");
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      setItems(await listOwnedMedia(brandId));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [brandId]);

  async function add() {
    if (!value.trim()) return;
    setError(null);
    try {
      await createOwnedMedia(brandId, mediaType, value.trim());
      setValue("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function remove(id: number) {
    await deleteOwnedMedia(id);
    await refresh();
  }

  return (
    <div>
      <div className="row">
        <div>
          <label>매체 유형</label>
          <select
            value={mediaType}
            onChange={(e) => setMediaType(e.target.value as MediaType)}
            style={{
              background: "#0f1115",
              color: "var(--text)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "9px 11px",
              fontSize: 14,
            }}
          >
            {MEDIA_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div style={{ flex: 1 }}>
          <label>도메인 또는 핸들 (예: example.com, @handle)</label>
          <input
            style={{ width: "100%" }}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={mediaType === "web" || mediaType === "blog" ? "example.com" : "@handle"}
          />
        </div>
        <button onClick={add} disabled={!value.trim()}>
          추가
        </button>
      </div>

      <div className="chips">
        {items.map((it) => (
          <span key={it.id} className="chip">
            <span className="badge">{it.media_type}</span> {it.domain_or_handle}{" "}
            <button
              onClick={() => remove(it.id)}
              style={{
                background: "transparent",
                color: "var(--muted)",
                padding: "0 4px",
                fontSize: 13,
              }}
              aria-label="remove"
            >
              ✕
            </button>
          </span>
        ))}
        {items.length === 0 && <span className="muted">등록된 온드미디어가 없습니다.</span>}
      </div>

      {error && <p className="error">⚠ {error}</p>}
    </div>
  );
}
