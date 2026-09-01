import { useEffect, useState } from "react";
import { FileImage, ImageOff, RefreshCw, X } from "lucide-react";

interface ImagePreviewCardProps { file: File; onChange: () => void; onRemove: () => void; }

const formatFileSize = (bytes: number) => bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
const imageType = (file: File) => file.type.replace("image/", "").toUpperCase() || "IMAGE";

const ImagePreviewCard = ({ file, onChange, onRemove }: ImagePreviewCardProps) => {
  const [imageUrl, setImageUrl] = useState<string>();
  const [dimensions, setDimensions] = useState("Reading dimensions…");
  const [previewUnavailable, setPreviewUnavailable] = useState(false);

  useEffect(() => {
    const objectUrl = URL.createObjectURL(file);
    setImageUrl(objectUrl); setDimensions("Reading dimensions…"); setPreviewUnavailable(false);
    const image = new Image();
    image.onload = () => setDimensions(`${image.naturalWidth.toLocaleString()} × ${image.naturalHeight.toLocaleString()}`);
    image.onerror = () => { setDimensions("Dimensions unavailable"); setPreviewUnavailable(true); };
    image.src = objectUrl;
    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  return (
    <article className="atlas-preview-card" aria-label={`Selected image: ${file.name}`}>
      <div className="atlas-preview-card__media">
        {imageUrl && !previewUnavailable ? <img src={imageUrl} alt={`Preview of ${file.name}`} onError={() => setPreviewUnavailable(true)} /> : <div className="atlas-preview-card__fallback"><ImageOff size={28} aria-hidden="true" /><span>Preview unavailable</span></div>}
      </div>
      <div className="atlas-preview-card__details">
        <span className="atlas-preview-card__label"><FileImage size={15} aria-hidden="true" /> Image selected</span>
        <h2 title={file.name}>{file.name}</h2>
        <dl><div><dt>Format</dt><dd>{imageType(file)}</dd></div><div><dt>Size</dt><dd>{formatFileSize(file.size)}</dd></div><div><dt>Dimensions</dt><dd>{dimensions}</dd></div></dl>
        <div className="atlas-preview-card__actions">
          <button type="button" onClick={onChange}><RefreshCw size={15} aria-hidden="true" /> Change image</button>
          <button type="button" onClick={onRemove} aria-label="Remove selected image"><X size={15} aria-hidden="true" /> Remove</button>
        </div>
      </div>
    </article>
  );
};

export default ImagePreviewCard;
