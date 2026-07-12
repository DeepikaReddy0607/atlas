import { useEffect, useState } from "react";

interface ImageViewerProps {
  file: File;
}

const ImageViewer = ({ file }: ImageViewerProps) => {
  const [imageUrl, setImageUrl] = useState("");

  useEffect(() => {
    const url = URL.createObjectURL(file);

    setImageUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [file]);

  return (
    <div
      className="
        flex
        h-full
        w-full
        items-center
        justify-center
        overflow-hidden
        bg-[var(--atlas-bg)]
      "
    >
      <img
        src={imageUrl}
        alt={file.name}
        className="
          max-h-full
          max-w-full
          object-contain
          select-none
        "
        draggable={false}
      />
    </div>
  );
};

export default ImageViewer;