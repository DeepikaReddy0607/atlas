interface SectionProps {
  title: string;
  children: React.ReactNode;
}

const Section = ({
  title,
  children,
}: SectionProps) => {
  return (
    <section className="mb-6">
      <h3
        className="
          mb-3
          text-xs
          font-semibold
          uppercase
          tracking-wider
          text-[var(--atlas-text-muted)]
        "
      >
        {title}
      </h3>

      <div
        className="
          rounded-lg
          border
          border-[var(--atlas-border)]
          bg-[var(--atlas-bg)]
          p-3
        "
      >
        {children}
      </div>
    </section>
  );
};

export default Section;