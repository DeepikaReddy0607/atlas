import {
  ShieldAlert,
  Network,
  Target,
  Lightbulb,
} from "lucide-react";

import { useAtlasAnalysis } from "../../hooks/useAtlasAnalysis";

const RiskPanel = () => {
  const { analysisResult } =
    useAtlasAnalysis();

  if (!analysisResult) {
    return (
      <div className="p-6 text-center text-[var(--atlas-text-muted)]">
        <ShieldAlert
          size={48}
          className="mx-auto mb-4 opacity-50"
        />

        <h2 className="text-lg font-semibold">
          No Risk Assessment
        </h2>

        <p className="mt-2 text-sm">
          Run an analysis to calculate network
          resilience and risk.
        </p>
      </div>
    );
  }

  const {
    risk,
    resilience,
  } = analysisResult;

  const ari = risk.ari;

  const riskLevel =
    risk.level?.toUpperCase() ??
    "UNKNOWN";

  const getRiskStyle = () => {
    switch (riskLevel) {
      case "HIGH":
        return {
          badge:
            "bg-red-500/15 text-red-400 border-red-500/30",
          ring:
            "border-red-500/40",
          text: "text-red-400",
        };

      case "MODERATE":
        return {
          badge:
            "bg-amber-500/15 text-amber-400 border-amber-500/30",
          ring:
            "border-amber-500/40",
          text: "text-amber-400",
        };

      case "LOW":
        return {
          badge:
            "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
          ring:
            "border-emerald-500/40",
          text: "text-emerald-400",
        };

      default:
        return {
          badge:
            "bg-slate-500/15 text-slate-400 border-slate-500/30",
          ring:
            "border-slate-500/40",
          text: "text-slate-400",
        };
    }
  };

  const riskStyle =
    getRiskStyle();

  const criticalNode =
    resilience.critical_node;

  return (
    <div
      className="
        h-full
        overflow-y-auto
        p-5
      "
    >
      {/* =====================================================
          HEADER
      ====================================================== */}

      <div className="flex items-start gap-3">
        <div
          className="
            rounded-lg
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-2
          "
        >
          <ShieldAlert size={18} />
        </div>

        <div>
          <h2 className="text-xl font-semibold">
            Risk & Resilience
          </h2>

          <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
            Network stability and infrastructure risk assessment
          </p>
        </div>
      </div>

      {/* =====================================================
          RISK OVERVIEW
      ====================================================== */}

      <section className="mt-6">
        <div
          className={`
            rounded-xl
            border
            ${riskStyle.ring}
            bg-[var(--atlas-bg)]
            p-5
          `}
        >
          <div className="flex items-center justify-between">
            <div>
              <p
                className="
                  text-xs
                  font-medium
                  uppercase
                  tracking-wide
                  text-[var(--atlas-text-muted)]
                "
              >
                Network Risk
              </p>

              <p
                className={`
                  mt-2
                  text-3xl
                  font-bold
                  ${riskStyle.text}
                `}
              >
                {riskLevel}
              </p>
            </div>

            <div
              className="
                flex
                h-20
                w-20
                items-center
                justify-center
                rounded-full
                border-4
                border-[var(--atlas-border)]
              "
            >
              <span className="text-lg font-semibold">
                {(ari * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div
            className={`
              mt-4
              inline-flex
              rounded-full
              border
              px-3
              py-1
              text-xs
              font-medium
              ${riskStyle.badge}
            `}
          >
            {riskLevel} RISK
          </div>
        </div>
      </section>

      {/* =====================================================
          ARI
      ====================================================== */}

      <section className="mt-6">
        <div
          className="
            rounded-xl
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-5
          "
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-[var(--atlas-text-muted)]">
                Adjusted Resilience Index
              </p>

              <p className="mt-1 text-3xl font-bold">
                {ari.toFixed(3)}
              </p>
            </div>

            <Target
              size={22}
              className="text-blue-400"
            />
          </div>

          <div
            className="
              mt-4
              h-2
              overflow-hidden
              rounded-full
              bg-[var(--atlas-border)]
            "
          >
            <div
              className="
                h-full
                rounded-full
                bg-blue-500
                transition-all
                duration-500
              "
              style={{
                width: `${Math.max(
                  0,
                  Math.min(100, ari * 100)
                )}%`,
              }}
            />
          </div>

          <div className="mt-2 flex justify-between text-xs text-[var(--atlas-text-muted)]">
            <span>0.0</span>
            <span>1.0</span>
          </div>
        </div>
      </section>

      {/* =====================================================
          RESILIENCE METRICS
      ====================================================== */}

      <section className="mt-6">
        <div className="mb-3 flex items-center gap-2">
          <Network size={15} />

          <span
            className="
              text-xs
              font-medium
              uppercase
              tracking-wide
              text-[var(--atlas-text-muted)]
            "
          >
            Resilience Structure
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Metric
            label="Components"
            value={
              resilience.connected_components
            }
          />

          <Metric
            label="Largest Component"
            value={
              resilience.largest_component
            }
          />
        </div>
      </section>

      {/* =====================================================
          CRITICAL NODE
      ====================================================== */}

      <section className="mt-3">
        <div
          className="
            rounded-xl
            border
            border-[var(--atlas-border)]
            bg-[var(--atlas-bg)]
            p-4
          "
        >
          <p className="text-xs text-[var(--atlas-text-muted)]">
            Most Critical Node
          </p>

          {criticalNode ? (
            <>
              <p className="mt-1 text-lg font-semibold">
                ({criticalNode[0]}, {criticalNode[1]})
              </p>

              <p className="mt-1 text-xs text-[var(--atlas-text-muted)]">
                Highest network criticality identified during analysis
              </p>
            </>
          ) : (
            <p className="mt-1 text-sm text-[var(--atlas-text-muted)]">
              No critical node identified.
            </p>
          )}
        </div>
      </section>

      {/* =====================================================
          RECOMMENDATION
      ====================================================== */}

      <section className="mt-6">
        <div
          className="
            rounded-xl
            border
            border-blue-500/20
            bg-blue-500/5
            p-5
          "
        >
          <div className="flex items-center gap-2">
            <Lightbulb
              size={18}
              className="text-blue-400"
            />

            <h3 className="font-semibold">
              Recommendation
            </h3>
          </div>

          <p className="mt-3 text-sm leading-6 text-[var(--atlas-text-muted)]">
            {risk.recommendation}
          </p>
        </div>
      </section>
    </div>
  );
};

/* ============================================================
   Metric
============================================================ */

interface MetricProps {
  label: string;
  value: number | string;
}

const Metric = ({
  label,
  value,
}: MetricProps) => {
  return (
    <div
      className="
        rounded-xl
        border
        border-[var(--atlas-border)]
        bg-[var(--atlas-bg)]
        p-4
      "
    >
      <p className="text-xs text-[var(--atlas-text-muted)]">
        {label}
      </p>

      <p className="mt-1 text-xl font-semibold">
        {value}
      </p>
    </div>
  );
};

export default RiskPanel;