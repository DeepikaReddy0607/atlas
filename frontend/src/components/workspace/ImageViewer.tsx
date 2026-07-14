import { useEffect, useState } from "react";

interface ImageViewerProps {
  file: File;
}

const ImageViewer = ({ file }: ImageViewerProps) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  useEffect(() => {
    const url = URL.createObjectURL(file);

    setImageUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  if (!imageUrl) {
    return null;
  }

  return (
    <div className="flex h-full w-full items-center justify-center">
      <img
        src={imageUrl}
        alt={file.name}
        className="max-h-full max-w-full object-contain"
      />
    </div>
  );
};

export default ImageViewer;