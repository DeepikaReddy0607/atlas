import { useRef } from "react";

import {
  ArrowRight,
  ChartNoAxesColumnIncreasing,
  FolderOpen,
  Layers3,
  Map,
  Network,
  Plus,
  Satellite,
  ShieldCheck,
} from "lucide-react";

interface EmptyWorkspaceProps {
  onFileSelected: (file: File) => void;
  onNewAnalysis: () => void;
}

const SUPPORTED_TYPES = [
  "image/png",
  "image/jpeg",
  "image/tiff",
];

const EmptyWorkspace = ({
  onFileSelected,
  onNewAnalysis,
}: EmptyWorkspaceProps) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
  const handleFile = (file: File | null) => {
    if (!file) return;

    if (!SUPPORTED_TYPES.includes(file.type)) {
      alert("Unsupported file format.");
      return;
    }

    onFileSelected(file);
  };

  const handleDrop = (
    event: React.DragEvent<HTMLDivElement>,
  ) => {
    event.preventDefault();

    handleFile(event.dataTransfer.files?.[0] ?? null);
  };

  return (
    <main
  className="
    relative
    h-full
    w-full
    overflow-hidden
    bg-white
    text-[#263238]
  "
  onDragOver={(event) => event.preventDefault()}
  onDrop={handleDrop}
>
      {/* =====================================================
          TECHNICAL BACKGROUND
      ===================================================== */}

      <div
        className="
          pointer-events-none
          absolute
          inset-0
          opacity-70
        "
        style={{
          backgroundImage: `
            radial-gradient(
              circle at 20% 25%,
              transparent 0,
              transparent 90px,
              rgba(82,111,75,0.08) 91px,
              transparent 92px
            ),
            radial-gradient(
              circle at 35% 75%,
              transparent 0,
              transparent 130px,
              rgba(82,111,75,0.06) 131px,
              transparent 132px
            ),
            linear-gradient(
              90deg,
              transparent 0,
              transparent 49.8%,
              rgba(82,111,75,0.05) 50%,
              transparent 50.2%
            ),
            linear-gradient(
              0deg,
              transparent 0,
              transparent 49.8%,
              rgba(82,111,75,0.05) 50%,
              transparent 50.2%
            )
          `,
          backgroundSize:
            "500px 500px, 700px 700px, 50% 100%, 100% 50%",
        }}
      />

      {/* =====================================================
          COORDINATE HUD
      ===================================================== */}

      <div
        className="
          pointer-events-none
          absolute
          left-10
          top-8
          z-10
          font-mono
          text-[9px]
          uppercase
          tracking-[0.22em]
          text-[#a8afb0]
        "
      >
        <div>34° 56′ 12″ N</div>
        <div>78° 14′ 45″ E</div>
      </div>

      <div
        className="
          pointer-events-none
          absolute
          right-8
          top-8
          z-10
          text-right
          font-mono
          text-[9px]
          uppercase
          tracking-[0.22em]
          text-[#a8afb0]
        "
      >
        <div>ATLAS / GEO-01</div>
        <div className="mt-1">NO REGION LOADED</div>
      </div>

      {/* =====================================================
          CONTENT
      ===================================================== */}

      <div
        className="
          relative
          z-10
          flex
          h-full
          min-h-0
          flex-col
          px-14
          pb-8
          pt-20
          xl:px-16
        "
      >
        <div
          className="
            flex
            min-h-0
            flex-1
            items-center
            gap-10
            xl:gap-14
          "
        >
          {/* =================================================
              LEFT HERO
          ================================================= */}

          <section
            className="
              flex
              min-w-0
              flex-1
              flex-col
              justify-center
              pl-2
              xl:max-w-[52%]
            "
          >
            {/* Status */}

            <div
              className="
                mb-8
                flex
                items-center
                gap-3
                font-mono
                text-[12px]
                font-medium
                uppercase
                tracking-[0.12em]
                text-[#526f4b]
              "
            >
              <span
                className="
                  h-2
                  w-2
                  rounded-full
                  bg-[#526f4b]
                "
              />

              <span>
                SYSTEM READY / GEOSPATIAL INTELLIGENCE
              </span>
            </div>

            {/* Main statement */}

            <h1
              className="
                max-w-[700px]
                text-[clamp(3rem,4.2vw,4.5rem)]
                font-semibold
                uppercase
                leading-[0.98]
                tracking-[-0.045em]
                text-[#263238]
              "
            >
              <span className="block">
                Understand the terrain.
              </span>

              <span className="block">
                Map the{" "}
                <span className="text-[#617f56]">
                  lifelines.
                </span>
              </span>

              <span className="block">
                Model the risk.
              </span>
            </h1>

            {/* Accent */}

            <div
              className="
                mb-7
                mt-9
                h-[3px]
                w-10
                bg-[#b08a32]
              "
            />

            {/* Description */}

            <p
              className="
                max-w-[620px]
                text-[17px]
                leading-7
                text-[#465258]
              "
            >
              AI-powered geospatial intelligence for
              infrastructure networks, terrain analysis,
              and resilience assessment.
              <br />
              Make informed decisions. Strengthen what matters.
            </p>

            {/* =================================================
                ACTIONS
            ================================================= */}

            <div className="mt-10 flex items-center gap-5">
              {/* New Analysis */}

              <button
                type="button"
                onClick={onNewAnalysis}
                className="
                  group
                  flex
                  h-[62px]
                  min-w-[235px]
                  items-center
                  justify-center
                  gap-4
                  rounded-[5px]
                  bg-[#617f56]
                  px-6
                  text-[14px]
                  font-semibold
                  uppercase
                  tracking-[0.06em]
                  text-white
                  shadow-sm
                  transition-all
                  duration-200
                  hover:bg-[#526f4b]
                  hover:shadow-md
                  active:scale-[0.99]
                "
              >
                <Plus
                  size={24}
                  strokeWidth={1.5}
                />

                <span>New Analysis</span>

                <ArrowRight
                  size={21}
                  strokeWidth={1.6}
                  className="
                    transition-transform
                    duration-200
                    group-hover:translate-x-1
                  "
                />
              </button>

              {/* Open Workspace */}

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="
                  flex
                  h-[62px]
                  min-w-[235px]
                  items-center
                  justify-center
                  gap-4
                  rounded-[5px]
                  border
                  border-[#bfc6c1]
                  bg-white/80
                  px-6
                  text-[14px]
                  font-semibold
                  uppercase
                  tracking-[0.06em]
                  text-[#263238]
                  transition-all
                  duration-200
                  hover:border-[#617f56]
                  hover:bg-white
                "
              >
                <FolderOpen
                  size={23}
                  strokeWidth={1.5}
                />

                <span>Open Workspace</span>
              </button>
            </div>

            {/* =================================================
                FEATURE STRIP
            ================================================= */}

            <div
              className="
                mt-10
                grid
                max-w-[700px]
                grid-cols-4
                border-t
                border-[#dfe4df]
                pt-7
              "
            >
              <Feature
                icon={<Satellite size={23} />}
                title="Satellite"
                subtitle="Intelligence"
                description="High-resolution imagery and AI segmentation"
              />

              <Feature
                icon={<Network size={23} />}
                title="Network"
                subtitle="Analysis"
                description="Extract, model and analyze infrastructure networks"
              />

              <Feature
                icon={<ShieldCheck size={23} />}
                title="Risk &"
                subtitle="Resilience"
                description="Identify critical points and simulate infrastructure failure"
              />

              <Feature
                icon={<ChartNoAxesColumnIncreasing size={23} />}
                title="Actionable"
                subtitle="Insights"
                description="Generate reports and support better decisions"
              />
            </div>
          </section>

          {/* =================================================
              REGION PREVIEW
          ================================================= */}

          <section
            className="
              relative
              hidden
              h-[min(72vh,710px)]
              w-[48%]
              max-w-[720px]
              min-w-[480px]
              overflow-hidden
              rounded-[10px]
              border
              border-[#d5dad5]
              bg-[#3d523b]
              shadow-[0_18px_45px_rgba(38,50,56,0.14)]
              xl:block
            "
          >
            {/* Map texture */}

            <div
              className="
                absolute
                inset-0
                opacity-80
              "
              style={{
                backgroundImage: `
                  radial-gradient(
                    ellipse at 20% 20%,
                    #718364 0%,
                    #465b43 28%,
                    transparent 50%
                  ),
                  radial-gradient(
                    ellipse at 80% 35%,
                    #263d2d 0%,
                    #40563e 30%,
                    transparent 60%
                  ),
                  radial-gradient(
                    ellipse at 45% 85%,
                    #68775c 0%,
                    #344a35 38%,
                    transparent 65%
                  ),
                  linear-gradient(
                    135deg,
                    #304630,
                    #52664b
                  )
                `,
              }}
            />

            {/* Grid */}

            <div
              className="
                absolute
                inset-0
                opacity-20
              "
              style={{
                backgroundImage: `
                  linear-gradient(
                    rgba(255,255,255,0.3) 1px,
                    transparent 1px
                  ),
                  linear-gradient(
                    90deg,
                    rgba(255,255,255,0.3) 1px,
                    transparent 1px
                  )
                `,
                backgroundSize: "60px 60px",
              }}
            />

            {/* =================================================
                NETWORK GRAPH
            ================================================= */}

            <svg
              viewBox="0 0 720 710"
              className="
                absolute
                inset-0
                h-full
                w-full
              "
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <g
                fill="none"
                stroke="rgba(232,242,220,0.85)"
                strokeWidth="2.5"
              >
                <path d="M70 145 L215 250 L330 195 L465 280 L650 150" />
                <path d="M215 250 L170 430 L330 520 L465 280" />
                <path d="M170 430 L75 570" />
                <path d="M330 520 L425 630" />
                <path d="M465 280 L535 455 L650 520" />
                <path d="M535 455 L620 390 L650 150" />
              </g>

              <g
                fill="#f3f7ed"
                stroke="#6f8d64"
                strokeWidth="3"
              >
                <circle cx="70" cy="145" r="7" />
                <circle cx="215" cy="250" r="10" />
                <circle cx="330" cy="195" r="7" />
                <circle cx="465" cy="280" r="10" />
                <circle cx="650" cy="150" r="7" />
                <circle cx="170" cy="430" r="8" />
                <circle cx="330" cy="520" r="9" />
                <circle cx="535" cy="455" r="8" />
                <circle cx="75" cy="570" r="6" />
                <circle cx="425" cy="630" r="6" />
                <circle cx="650" cy="520" r="7" />
                <circle cx="620" cy="390" r="7" />
              </g>
            </svg>

            {/* Region label */}

            <div
              className="
                absolute
                left-6
                top-6
                rounded-[4px]
                bg-white/90
                px-3
                py-2
                text-[13px]
                font-medium
                uppercase
                tracking-[0.08em]
                text-[#263238]
              "
            >
              Region Preview
            </div>

            {/* Layer button */}

            <button
              type="button"
              className="
                absolute
                right-6
                top-6
                flex
                h-11
                w-11
                items-center
                justify-center
                rounded-[5px]
                bg-white
                text-[#344047]
                shadow-sm
                transition
                hover:bg-[#f4f6f3]
              "
              aria-label="Map layers"
            >
              <Layers3 size={22} />
            </button>

            {/* Zoom controls */}

            <div
              className="
                absolute
                bottom-7
                left-6
                flex
                flex-col
                overflow-hidden
                rounded-[5px]
                bg-white
                shadow-sm
              "
            >
              <button
                type="button"
                className="
                  flex
                  h-11
                  w-11
                  items-center
                  justify-center
                  border-b
                  border-[#e1e5e1]
                  text-xl
                  hover:bg-[#f5f7f4]
                "
              >
                +
              </button>

              <button
                type="button"
                className="
                  flex
                  h-11
                  w-11
                  items-center
                  justify-center
                  text-xl
                  hover:bg-[#f5f7f4]
                "
              >
                −
              </button>
            </div>

            {/* Scale */}

            <div
              className="
                absolute
                bottom-9
                left-20
                flex
                items-end
                gap-3
                text-[11px]
                text-white
              "
            >
              <span>0</span>

              <div
                className="
                  h-[2px]
                  w-[260px]
                  bg-white
                "
              />

              <span>2 km</span>
            </div>

            {/* Current region card */}

            <div
              className="
                absolute
                bottom-6
                right-6
                w-[220px]
                rounded-[7px]
                bg-white
                p-6
                shadow-lg
              "
            >
              <div
                className="
                  mb-5
                  flex
                  items-center
                  gap-3
                  text-[12px]
                  font-semibold
                  uppercase
                  tracking-[0.08em]
                  text-[#344047]
                "
              >
                <Map size={18} />

                <span>Current Region</span>
              </div>

              <div
                className="
                  font-mono
                  text-[13px]
                  leading-7
                  text-[#536067]
                "
              >
                <div>34° 56′ 12″ N</div>
                <div>78° 14′ 45″ E</div>
              </div>

              <div
                className="
                  mt-4
                  text-[10px]
                  uppercase
                  tracking-[0.12em]
                  text-[#7d878b]
                "
              >
                Zoom Level 13.2
              </div>
            </div>
          </section>
        </div>

        {/* ===================================================
            BOTTOM TECHNICAL LINE
        =================================================== */}

        <div
          className="
            mt-5
            flex
            items-center
            justify-between
            border-t
            border-[#dfe4df]
            pt-3
            font-mono
            text-[9px]
            uppercase
            tracking-[0.16em]
            text-[#788287]
          "
        >
          <span>Input / Satellite Imagery</span>

          <span>Engine Standby</span>
        </div>
      </div>
    </main>
  );
};

interface FeatureProps {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  description: string;
}

const Feature = ({
  icon,
  title,
  subtitle,
  description,
}: FeatureProps) => {
  return (
    <div className="pr-5">
      <div
        className="
          mb-3
          flex
          items-center
          gap-3
          text-[#526f4b]
        "
      >
        {icon}

        <div
          className="
            text-[10px]
            font-semibold
            uppercase
            leading-4
            tracking-[0.07em]
          "
        >
          <div>{title}</div>
          <div>{subtitle}</div>
        </div>
      </div>

      <p
        className="
          max-w-[145px]
          text-[9px]
          leading-4
          text-[#737d81]
        "
      >
        {description}
      </p>
    </div>
  );
};

export default EmptyWorkspace;