interface RowProps {
  label: string;
  value: React.ReactNode;
}

const Row = ({
  label,
  value,
}: RowProps) => {
  return (
    <div
      className="
        flex
        items-center
        justify-between
        py-1.5
        text-sm
      "
    >
      <span className="text-[var(--atlas-text-muted)]">
        {label}
      </span>

      <span className="font-medium">
        {value}
      </span>
    </div>
  );
};

export default Row;