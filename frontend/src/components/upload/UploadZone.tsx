import { useRef, useState } from "react";
import { Check, ImageUp, UploadCloud } from "lucide-react";

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
}

const SUPPORTED_TYPES = [
  "image/png",
  "image/jpeg",
  "image/tiff",
];

const SUPPORTED_EXTENSIONS = [
  ".png",
  ".jpg",
  ".jpeg",
  ".tif",
  ".tiff",
];

const UploadZone = ({ onFileSelected }: UploadZoneProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File | null) => {
    if (!file) return;

    const validType = SUPPORTED_TYPES.includes(file.type);

    const validExtension = SUPPORTED_EXTENSIONS.some((extension) =>
      file.name.toLowerCase().endsWith(extension),
    );

    if (!validType && !validExtension) {
      alert("Unsupported file format. Please select PNG, JPEG, or TIFF.");
      return;
    }

    setSelectedFile(file);
    onFileSelected(file);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(false);

    const file = event.dataTransfer.files[0];

    handleFile(file);
  };

  const handleBrowse = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    handleFile(file ?? null);

    event.target.value = "";
  };

  const openFilePicker = () => {
    inputRef.current?.click();
  };

  return (
    <>
      <input
        ref={inputRef}
        hidden
        type="file"
        accept=".png,.jpg,.jpeg,.tif,.tiff,image/png,image/jpeg,image/tiff"
        onChange={handleBrowse}
      />

      <div
        onDragOver={(event) => {
          event.preventDefault();
          event.stopPropagation();
        }}
        onDragEnter={(event) => {
          event.preventDefault();
          event.stopPropagation();
          setIsDragging(true);
        }}
        onDragLeave={(event) => {
          event.preventDefault();
          event.stopPropagation();

          if (event.currentTarget === event.target) {
            setIsDragging(false);
          }
        }}
        onDrop={handleDrop}
        className={`
          flex
          h-full
          min-h-[285px]
          w-full
          flex-col
          items-center
          justify-center
          border
          border-dashed
          px-6
          text-center
          transition-colors
          duration-200
          ${
            isDragging
              ? "border-[#58784e] bg-[#f3f7f1]"
              : "border-[#aebaa9] bg-[#fcfdfb]"
          }
        `}
      >
        {selectedFile ? (
          <>
            <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-full border border-[#c9d5c5] bg-[#f3f7f1]">
              <Check
                size={25}
                className="text-[#58784e]"
              />
            </div>

            <p className="font-mono text-[10px] font-bold uppercase tracking-[0.16em] text-[#58784e]">
              Imagery selected
            </p>

            <p className="mt-3 max-w-md truncate text-base font-medium text-[#35403b]">
              {selectedFile.name}
            </p>

            <p className="mt-2 font-mono text-[9px] uppercase tracking-[0.12em] text-[#89938e]">
              {formatFileSize(selectedFile.size)}
            </p>

            <button
              type="button"
              onClick={openFilePicker}
              className="
                mt-6
                border
                border-[#ccd5c9]
                bg-white
                px-5
                py-2.5
                text-[10px]
                font-semibold
                uppercase
                tracking-[0.12em]
                text-[#58645f]
                transition-colors
                hover:border-[#58784e]
                hover:text-[#58784e]
              "
            >
              Replace image
            </button>
          </>
        ) : (
          <>
            <div
              className={`
                mb-6
                flex
                h-16
                w-16
                items-center
                justify-center
                border
                transition-colors
                ${
                  isDragging
                    ? "border-[#58784e] bg-[#eef5eb]"
                    : "border-[#d3ddd0] bg-[#f5f8f3]"
                }
              `}
            >
              {isDragging ? (
                <UploadCloud
                  size={29}
                  className="text-[#58784e]"
                />
              ) : (
                <ImageUp
                  size={29}
                  className="text-[#58784e]"
                />
              )}
            </div>

            <p className="font-mono text-xs font-bold uppercase tracking-[0.16em] text-[#4e6250]">
              {isDragging
                ? "Release to import imagery"
                : "Drop satellite image here"}
            </p>

            <p className="mt-3 text-sm text-[#7a847f]">
              or
            </p>

            <button
              type="button"
              onClick={openFilePicker}
              className="
                mt-2
                border-b
                border-[#7d9675]
                pb-0.5
                text-xs
                font-semibold
                uppercase
                tracking-[0.10em]
                text-[#58784e]
                transition-colors
                hover:border-[#405b3a]
                hover:text-[#405b3a]
              "
            >
              Browse files
            </button>

            <div className="mt-7 flex items-center gap-3 font-mono text-[9px] font-semibold uppercase tracking-[0.12em] text-[#9aa29d]">
              <span>PNG</span>
              <span className="text-[#c6cdc5]">•</span>
              <span>JPEG</span>
              <span className="text-[#c6cdc5]">•</span>
              <span>TIFF</span>
            </div>
          </>
        )}
      </div>
    </>
  );
};

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export default UploadZone;