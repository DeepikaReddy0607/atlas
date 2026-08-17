import type { SimulationScenario } from "../../context/SimulationContext";

interface Props {
  title: string;
  description: string;
  scenario: SimulationScenario;
  selected: boolean;
  onClick: () => void;
}

const ScenarioCard = ({
  title,
  description,
  selected,
  onClick,
}: Props) => {
  return (
    <button
      onClick={onClick}
      className={`
        w-full
        rounded-lg
        border
        p-4
        text-left
        transition-all

        ${
          selected
            ? "border-blue-500 bg-blue-500/10"
            : "border-[var(--atlas-border)] bg-[var(--atlas-bg)]"
        }
      `}
    >
      <h3 className="font-semibold">
        {title}
      </h3>

      <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
        {description}
      </p>
    </button>
  );
};

export default ScenarioCard;