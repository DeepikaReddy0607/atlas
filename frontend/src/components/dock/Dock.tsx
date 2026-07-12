import DockItem from "./DockItem";
import { dockItems } from "./dockItems";

const Dock = () => {
  return (
    <aside
      className="
        flex
        w-[var(--dock-width)]
        flex-col
        items-center
        justify-between
        border-r
        border-[var(--atlas-border)]
        bg-[var(--atlas-bg)]
        py-4
      "
    >
      <div className="flex flex-col items-center gap-3">
        {dockItems.map((item, index) => (
          <DockItem
            key={item.id}
            icon={item.icon}
            label={item.label}
            active={index === 0}
          />
        ))}
      </div>
    </aside>
  );
};

export default Dock;