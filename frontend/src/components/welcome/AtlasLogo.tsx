type AtlasLogoSize = "default" | "compact" | "large";

interface AtlasLogoProps {
  size?: AtlasLogoSize;
  showDescriptor?: boolean;
  animated?: boolean;
}

const sizeMap = {
  compact: {
    mark: "h-8 w-8",
    wordmark: "text-lg",
    descriptor: "text-[10px]",
  },
  default: {
    mark: "h-10 w-10",
    wordmark: "text-xl",
    descriptor: "text-[11px]",
  },
  large: {
    mark: "h-28 w-28 sm:h-32 sm:w-32",
    wordmark: "text-6xl sm:text-7xl lg:text-8xl",
    descriptor: "text-xs sm:text-sm",
  },
};

const AtlasLogo = ({
  size = "default",
  showDescriptor = false,
  animated = false,
}: AtlasLogoProps) => {
  const styles = sizeMap[size];

  return (
    <div
      className={`atlas-logo flex flex-col items-center select-none ${
        animated ? "atlas-logo--animated" : ""
      }`}
      aria-label="ATLAS"
    >
      <svg
        className={styles.mark}
        viewBox="0 0 120 100"
        fill="none"
        aria-hidden="true"
      >
        {/* Main geometric ATLAS mark */}
        <path
          className="atlas-logo__line atlas-logo__line--one"
          d="M18 78 L45 25 L67 65"
        />

        <path
          className="atlas-logo__line atlas-logo__line--two"
          d="M67 65 L84 34 L103 78"
        />

        <path
          className="atlas-logo__line atlas-logo__line--three"
          d="M45 25 L60 54 L84 34"
        />

        <path
          className="atlas-logo__base"
          d="M18 78 H103"
        />

        <circle
          className="atlas-logo__node atlas-logo__node--one"
          cx="45"
          cy="25"
          r="5"
        />

        <circle
          className="atlas-logo__node atlas-logo__node--two"
          cx="67"
          cy="65"
          r="4"
        />

        <circle
          className="atlas-logo__node atlas-logo__node--three"
          cx="84"
          cy="34"
          r="4"
        />

        <circle
          className="atlas-logo__node atlas-logo__node--four"
          cx="18"
          cy="78"
          r="4"
        />

        <circle
          className="atlas-logo__node atlas-logo__node--five"
          cx="103"
          cy="78"
          r="4"
        />
      </svg>

      <span
        className={`${styles.wordmark} mt-3 font-semibold leading-none tracking-[0.28em] text-[#20292d]`}
      >
        ATLAS
      </span>

      {showDescriptor && (
        <span
          className={`${styles.descriptor} mt-3 font-medium uppercase tracking-[0.22em] text-[#59645e]`}
        >
          Automated Terrain &amp; Lifeline Analysis
        </span>
      )}
    </div>
  );
};

export default AtlasLogo;