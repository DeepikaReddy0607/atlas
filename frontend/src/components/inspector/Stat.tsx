interface StatProps {
  label: string;
  value: string | number;
}

const Stat = ({
  label,
  value,
}: StatProps) => {
  return (
    <div className="flex justify-between py-1">
      <span className="text-sm text-[var(--atlas-text-muted)]">
        {label}
      </span>

      <span className="font-medium">
        {value}
      </span>
    </div>
  );
};

export default Stat;