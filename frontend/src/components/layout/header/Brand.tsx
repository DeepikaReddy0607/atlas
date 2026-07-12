const Brand = () => {
  return (
    <div className="flex select-none flex-col justify-center">
      <div className="flex items-center gap-2">

        {/* Temporary logo */}
        <div className="h-3 w-3 rounded-full bg-[var(--atlas-primary)]" />

        <h1
          className="
            text-lg
            font-bold
            tracking-wide
            text-[var(--atlas-text)]
          "
        >
          ATLAS
        </h1>

      </div>

      <p
        className="
          mt-0.5
          text-xs
          text-[var(--atlas-text-muted)]
        "
      >
        Infrastructure Intelligence
      </p>
    </div>
  );
};

export default Brand;