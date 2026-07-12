import { Info } from "lucide-react";

const EmptyInspector = () => {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-[var(--atlas-border)] px-5 py-4">
        <h2 className="text-sm font-semibold text-[var(--atlas-text)]">
          Inspector
        </h2>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
        <Info
          size={40}
          className="mb-4 text-[var(--atlas-text-muted)]"
        />

        <h3 className="mb-2 text-lg font-medium">
          Nothing Selected
        </h3>

        <p className="text-sm leading-6 text-[var(--atlas-text-muted)]">
          Upload an image or select an object to inspect its
          metadata, AI predictions, topology and simulation results.
        </p>
      </div>
    </div>
  );
};

export default EmptyInspector;