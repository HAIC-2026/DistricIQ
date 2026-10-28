import type { Chamber } from "@/types";
export function DistrictSelector({
  chamber,
  number,
  onChamber,
  onNumber,
}: {
  chamber: Chamber;
  number: number;
  onChamber: (v: Chamber) => void;
  onNumber: (v: number) => void;
}) {
  return (
    <div className="district-controls">
      <div className="segmented" aria-label="Legislative chamber">
        {(["house", "senate"] as const).map((c) => (
          <button
            key={c}
            aria-pressed={c === chamber}
            className={c === chamber ? "selected" : ""}
            onClick={() => onChamber(c)}
          >
            {c === "house" ? "House" : "Senate"}
            <span>{c === "house" ? 51 : 25}</span>
          </button>
        ))}
      </div>
      <label className="select-label">
        <span className="sr-only">Select district</span>
        <select
          value={number}
          onChange={(e) => onNumber(Number(e.target.value))}
        >
          {Array.from({ length: chamber === "house" ? 51 : 25 }, (_, i) => (
            <option key={i + 1} value={i + 1}>
              {chamber === "house" ? "House" : "Senate"} District {i + 1}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
