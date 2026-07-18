import { useEffect, useRef, useState } from "react";

type ScannerStatus = "idle" | "image-ready" | "confirmed";

type BallotScannerProps = {
  focusRing: string;
  onConfirmProp36: () => void;
};

export function BallotScanner({ focusRing, onConfirmProp36 }: BallotScannerProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [status, setStatus] = useState<ScannerStatus>("idle");
  const [fileName, setFileName] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [message, setMessage] = useState<string>(
    "Capture an unmarked ballot or official sample-ballot image. The image is kept only in browser memory for this session.",
  );

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  function clearImage() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setFileName(null);
    setStatus("idle");
    setMessage(
      "Capture an unmarked ballot or official sample-ballot image. The image is kept only in browser memory for this session.",
    );
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function handleImageUpload(file: File | undefined) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      clearImage();
      setMessage("Please choose an image file. PDFs and documents are not accepted in the scanner UI.");
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFileName(file.name || "Captured ballot image");
    setPreviewUrl(URL.createObjectURL(file));
    setStatus("image-ready");
    setMessage(
      "Image loaded in memory only. OCR is not connected yet, so confirm the supported demo measure manually.",
    );
  }

  function confirmProp36() {
    setStatus("confirmed");
    setMessage(
      "Confirmed: Proposition 36. Its reviewed corpus is embedded; select issue lenses and inspect the cited research.",
    );
    onConfirmProp36();
  }

  return (
    <section
      aria-labelledby="scanner-heading"
      className="rounded-lg border border-[#c3d1c8] bg-white/90 p-5 shadow-sm"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#52685c]">
            Phase 3 scanner prototype
          </p>
          <h2 id="scanner-heading" className="mt-1 text-xl font-semibold text-[#191815]">
            Scan a ballot item
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-[#53675b]">
            Use an unmarked ballot or official sample ballot. BallotSense does not read filled
            bubbles, store photos, or infer vote choices.
          </p>
        </div>
        <span className="rounded-full bg-[#fff6df] px-3 py-1 text-xs font-semibold text-[#6c5628]">
          Manual confirmation only
        </span>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[0.75fr_1fr]">
        <div className="rounded-md border border-dashed border-[#9fb9ab] bg-[#f8fff9] p-4">
          <input
            ref={fileInputRef}
            accept="image/*"
            capture="environment"
            className="sr-only"
            id="ballot-scanner-image"
            onChange={(event) => handleImageUpload(event.currentTarget.files?.[0])}
            type="file"
          />
          <label
            className={`flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-md border border-[#d2dfd6] bg-white px-4 py-6 text-center transition hover:bg-[#edf5ef] ${focusRing}`}
            htmlFor="ballot-scanner-image"
          >
            <span aria-hidden="true" className="text-4xl">
              📷
            </span>
            <span className="mt-3 font-semibold text-[#245c4d]">
              Capture or upload ballot image
            </span>
            <span className="mt-2 max-w-xs text-sm leading-6 text-[#665f54]">
              Mobile browsers should offer the rear camera. Desktop browsers open a file picker.
            </span>
          </label>
          {previewUrl && (
            <div className="mt-4">
              <img
                alt="Temporary in-memory ballot preview"
                className="max-h-64 w-full rounded-md border border-[#d2dfd6] object-contain"
                src={previewUrl}
              />
              <p className="mt-2 break-all text-xs text-[#665f54]">{fileName}</p>
            </div>
          )}
        </div>

        <div className="rounded-md border border-[#e0d4c1] bg-[#fffbf2] p-4">
          <h3 className="font-semibold text-[#191815]">Privacy and confirmation gate</h3>
          <ul className="mt-3 grid gap-2 text-sm leading-6 text-[#665f54]">
            <li>No image is written to local storage.</li>
            <li>No image is sent to the backend in this UI-only phase.</li>
            <li>Future OCR must process images in memory and discard them immediately.</li>
            <li>Users must confirm detected contests before research begins.</li>
          </ul>
          <p
            className="mt-4 rounded-md border border-[#d2dfd6] bg-white p-3 text-sm leading-6 text-[#405349]"
            role="status"
          >
            {message}
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              className={`rounded-md bg-[#245c4d] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#19483c] disabled:cursor-not-allowed disabled:bg-[#9aaca3] ${focusRing}`}
              disabled={status === "idle"}
              onClick={confirmProp36}
              type="button"
            >
              Confirm Proposition 36
            </button>
            <button
              className={`rounded-md border border-[#9c8f7c] px-4 py-2 text-sm font-semibold text-[#453f36] transition hover:bg-[#efe6d7] disabled:cursor-not-allowed disabled:opacity-60 ${focusRing}`}
              disabled={status === "idle"}
              onClick={clearImage}
              type="button"
            >
              Discard image
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
