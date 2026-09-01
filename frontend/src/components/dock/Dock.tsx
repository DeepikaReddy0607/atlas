import DockItem from "./DockItem";
import { dockItems } from "./dockItems";
import { useDock } from "../../context/DockContext";

const Dock = () => {
  const {
    activeTab,
    setActiveTab,
  } = useDock();

  return (
    <aside
      className="
        flex
        h-full
        w-full
        flex-col
        items-center
        bg-[#030B07]
      "
    >
      <nav
        className="
          flex
          w-full
          flex-1
          flex-col
          items-center
        "
        aria-label="ATLAS navigation"
      >
        {dockItems.map((item) => (
          <DockItem
            key={item.id}
            icon={item.icon}
            label={item.label}
            active={activeTab === item.id}
            onClick={() => setActiveTab(item.id)}
          />
        ))}
      </nav>

      {/* Dock footer */}

      <div
        className="
          flex
          h-[58px]
          w-full
          items-center
          justify-center
          border-t
          border-[#183522]
        "
      >
        <div className="flex flex-col items-center gap-1">
          <span
            className="
              h-[6px]
              w-[6px]
              rounded-full
              bg-[#8BFF3D]
              shadow-[0_0_10px_rgba(139,255,61,0.65)]
            "
          />

          <span
            className="
              font-mono
              text-[7px]
              uppercase
              tracking-[0.18em]
              text-[#4F6755]
            "
          >
            GEO-01
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Dock;