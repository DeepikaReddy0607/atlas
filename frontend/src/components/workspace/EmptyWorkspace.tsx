import { UploadCloud } from "lucide-react";

const EmptyWorkspace = () => {
  return (
    <div className="flex h-full items-center justify-center p-10">
      <div
        className="
          flex
          h-[520px]
          w-full
          max-w-5xl
          flex-col
          items-center
          justify-center
          rounded-[var(--radius-lg)]
          border-2
          border-dashed
          border-[var(--atlas-border)]
          bg-[var(--atlas-surface)]
          transition-all
          duration-200
          hover:border-[var(--atlas-primary)]
        "
      >
        <div
          className="
            mb-6
            flex
            h-20
            w-20
            items-center
            justify-center
            rounded-full
            bg-[var(--atlas-bg)]
          "
        >
          <UploadCloud
            size={36}
            className="text-[var(--atlas-primary)]"
          />
        </div>

        <h2 className="mb-3 text-3xl font-semibold">
          Start a New Analysis
        </h2>

        <p className="mb-8 max-w-xl text-center text-[var(--atlas-text-muted)]">
          Upload satellite imagery to begin AI-powered road extraction,
          topology analysis, resilience simulation and infrastructure
          intelligence.
        </p>

        <button
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
          Upload Satellite Image
        </button>

        <div className="mt-10 text-sm text-[var(--atlas-text-muted)]">
          Supported formats: GeoTIFF • PNG • JPEG
        </div>
      </div>
    </div>
  );
};

export default EmptyWorkspace;