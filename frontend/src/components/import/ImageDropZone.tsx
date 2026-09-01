import {
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type KeyboardEvent,
} from "react";

import { ImageUp } from "lucide-react";
import { toast } from "sonner";

interface ImageDropZoneProps {
  onFileSelected: (file: File) => void;
}

const supportedTypes = new Set([
  "image/jpeg",
  "image/png",
  "image/tiff",
  "image/webp",
]);

const ImageDropZone = ({
  onFileSelected,
}: ImageDropZoneProps) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);

  const selectFile = (file: File | undefined) => {
    if (!file) return;

    if (!supportedTypes.has(file.type)) {
      toast.error("Unsupported image format.", {
        description:
          "Choose a JPG, PNG, WEBP, or TIFF image.",
      });

      return;
    }

    onFileSelected(file);
  };

  const handleInput = (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    selectFile(event.target.files?.[0]);

    event.target.value = "";
  };

  const handleDrop = (
    event: DragEvent<HTMLDivElement>,
  ) => {
    event.preventDefault();

    setIsDragging(false);

    selectFile(event.dataTransfer.files[0]);
  };

  const handleKeyDown = (
    event: KeyboardEvent<HTMLDivElement>,
  ) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();

      inputRef.current?.click();
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        id="atlas-image-upload"
        className="sr-only"
        type="file"
        accept=".jpg,.jpeg,.png,.webp,.tif,.tiff"
        onChange={handleInput}
      />

      <div
        className={[
          "atlas-import-dropzone",
          isDragging
            ? "atlas-import-dropzone--active"
            : "",
        ].join(" ")}
        role="button"
        tabIndex={0}
        aria-label="Select a satellite image"
        onClick={() => inputRef.current?.click()}
        onKeyDown={handleKeyDown}
        onDragOver={(event) => {
          event.preventDefault();
        }}
        onDragEnter={() => {
          setIsDragging(true);
        }}
        onDragLeave={(event) => {
          if (
            event.currentTarget === event.target
          ) {
            setIsDragging(false);
          }
        }}
        onDrop={handleDrop}
      >

        <div className="atlas-import-dropzone__inner">

          <div className="atlas-import-dropzone__icon">
            <ImageUp
              size={30}
              strokeWidth={1.45}
              aria-hidden="true"
            />

            <span>+</span>
          </div>

          <p className="atlas-import-dropzone__title">
            Drop satellite image here
          </p>

          <p className="atlas-import-dropzone__hint">
            or{" "}
            <span>
              browse files
            </span>{" "}
            from your device
          </p>

        </div>

        <span
          className="atlas-import-dropzone__corner atlas-import-dropzone__corner--tl"
          aria-hidden="true"
        />

        <span
          className="atlas-import-dropzone__corner atlas-import-dropzone__corner--tr"
          aria-hidden="true"
        />

        <span
          className="atlas-import-dropzone__corner atlas-import-dropzone__corner--bl"
          aria-hidden="true"
        />

        <span
          className="atlas-import-dropzone__corner atlas-import-dropzone__corner--br"
          aria-hidden="true"
        />

      </div>
    </>
  );
};

export default ImageDropZone;