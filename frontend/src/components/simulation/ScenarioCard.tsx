import type { SimulationScenario } from "../../context/SimulationContext";

interface Props {
  title: string;
  subtitle: string;
  description: string;
  scenario: SimulationScenario;
  selected: boolean;
  onClick: () => void;
}

const ScenarioCard = ({
  title,
  subtitle,
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
      <h3 className="text-based font-semibold">
        {title}
      </h3>
        <p className="mt-1 text-sm font-medium text-blue-400">
          {subtitle}
        </p>
      <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
        {description}
      </p>
    </button>
  );
};

export default ScenarioCard;