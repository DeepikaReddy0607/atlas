import { Image as ImageIcon, CheckCircle, Clock } from "lucide-react";
import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";
import Row from "./Row";
const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024)
    return `${(bytes / 1024).toFixed(1)} KB`;

  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const ImageInformationPanel = () => {
  const {
    selectedFile,
    analysisResult,
  } = useAtlasAnalysis();

  if (!selectedFile) {
    return (
      <div className="p-6 text-center text-[var(--atlas-text-muted)]">
        <ImageIcon
          size={48}
          className="mx-auto mb-4 opacity-50"
        />

        <h2 className="text-lg font-semibold">
          No Image Selected
        </h2>

        <p className="mt-2 text-sm">
          Upload a satellite image to view its
          metadata.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-5">

      <div>
        <h2 className="text-xl font-semibold">
          Image Information
        </h2>

        <p className="text-sm text-[var(--atlas-text-muted)]">
          Uploaded satellite image metadata
        </p>
      </div>

      {/* Thumbnail */}

      <div className="overflow-hidden rounded-lg border border-[var(--atlas-border)]">
        <img
          src={URL.createObjectURL(selectedFile)}
          alt="Satellite"
          className="aspect-square w-full object-cover"
        />
      </div>

      {/* Metadata */}

      <div className="space-y-3 rounded-lg border border-[var(--atlas-border)] p-4">

        <Row
          label="Filename"
          value={selectedFile.name}
        />

        <Row
          label="File Size"
          value={formatFileSize(selectedFile.size)}
        />

        <Row
          label="File Type"
          value={selectedFile.type || "Unknown"}
        />

        <Row
          label="Status"
          value={
            analysisResult ? (
              <span className="flex items-center gap-2 text-green-400">
                <CheckCircle size={16} />
                Analysis Complete
              </span>
            ) : (
              <span className="flex items-center gap-2 text-yellow-400">
                <Clock size={16} />
                Waiting for Analysis
              </span>
            )
          }
        />

      </div>

      {analysisResult && (
        <div className="space-y-3 rounded-lg border border-[var(--atlas-border)] p-4">

          <h3 className="font-semibold">
            AI Summary
          </h3>

          <Row
            label="Model"
            value={analysisResult.segmentation.model_name}
          />

          <Row
            label="Inference"
            value={`${analysisResult.segmentation.inference_time_ms.toFixed(1)} ms`}
          />

          <Row
            label="Risk"
            value={analysisResult.risk.level}
          />

          <Row
            label="ARI"
            value={analysisResult.risk.ari.toFixed(3)}
          />

        </div>
      )}
    </div>
  );
};

export default ImageInformationPanel;