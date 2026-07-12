import { useRef, useState } from "react";
import { ImageUp } from "lucide-react";

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
}

const SUPPORTED_TYPES = [
  "image/png",
  "image/jpeg",
  "image/tiff",
];

const UploadZone = ({ onFileSelected }: UploadZoneProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File | null) => {
    if (!file) return;

    if (!SUPPORTED_TYPES.includes(file.type)) {
      alert("Unsupported file format.");
      return;
    }

    onFileSelected(file);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];

    handleFile(file);
  };

  const handleBrowse = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    handleFile(file ?? null);
  };

  return (
    <>
      <input
        ref={inputRef}
        hidden
        type="file"
        accept=".png,.jpg,.jpeg,.tif,.tiff"
        onChange={handleBrowse}
      />

      <div
        onDragOver={(e) => e.preventDefault()}
        onDragEnter={() => setIsDragging(true)}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          flex
          h-full
          w-full
          cursor-pointer
          flex-col
          items-center
          justify-center
          rounded-[var(--radius-lg)]
          border-2
          border-dashed
          transition-all
          duration-200

          ${
            isDragging
              ? "border-[var(--atlas-primary)] bg-[var(--atlas-elevated)]"
              : "border-[var(--atlas-border)] bg-[var(--atlas-surface)] hover:border-[var(--atlas-primary)]"
          }
        `}
      >
        <ImageUp
          size={54}
          className="mb-6 text-[var(--atlas-primary)]"
        />

        <h2 className="mb-3 text-2xl font-semibold">
          Drop Satellite Image
        </h2>

        <p className="mb-6 text-center text-[var(--atlas-text-muted)]">
          Drag & drop imagery here or click to browse.
        </p>

        <button
          type="button"
          className="
            rounded-[var(--radius-md)]
            bg-[var(--atlas-primary)]
            px-6
            py-3
            font-medium
            text-white
            transition-all
            duration-200
            hover:brightness-110
          "
        >
          Browse Files
        </button>

        <p className="mt-8 text-sm text-[var(--atlas-text-muted)]">
          Supported formats: PNG • JPEG • TIFF
        </p>
      </div>
    </>
  );
};

export default UploadZone;