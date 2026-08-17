import { Play } from "lucide-react";

interface Props {
  onClick: () => void;
  disabled?: boolean;
}

const RunSimulationButton = ({
  onClick,
  disabled,
}: Props) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="
        flex
        w-full
        items-center
        justify-center
        gap-2
        rounded-lg
        bg-blue-600
        px-4
        py-3
        font-medium
        text-white
        transition
        hover:bg-blue-700
        disabled:cursor-not-allowed
        disabled:opacity-50
      "
    >
      <Play size={18} />

      Run Simulation
    </button>
  );
};

export default RunSimulationButton;