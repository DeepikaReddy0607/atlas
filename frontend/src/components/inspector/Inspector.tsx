import EmptyInspector from "./EmptyInspector";

const Inspector = () => {
  return (
    <aside
      className="
        w-[var(--inspector-width)]
        border-l
        border-[var(--atlas-border)]
        bg-[var(--atlas-surface)]
      "
    >
      <EmptyInspector />
    </aside>
  );
};

export default Inspector;