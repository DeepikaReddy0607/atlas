import { useEffect, useRef, useState } from "react";
import { Check, RotateCcw } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";

import AtlasLogo from "../welcome/AtlasLogo";
import "./analysis-pipeline.css";

interface AnalysisPipelineProps {
  loading: boolean;
  error: string | null;
  complete: boolean;
  onComplete: () => void;
  onRetry: () => void;
}

const stages = [
  "Image Ingest",
  "AI Segmentation",
  "Road Extraction",
  "Skeletonization",
  "Topology Graph",
  "Criticality Analysis",
  "Risk & Resilience",
];

const STAGE_INTERVAL = 850;
const COMPLETION_DELAY = 420;

const AnalysisPipeline = ({ loading, error, complete, onComplete, onRetry }: AnalysisPipelineProps) => {
  const [activeStage, setActiveStage] = useState(0);
  const completedRef = useRef(false);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    if (!loading || complete || error) return;

    setActiveStage(0);
    const interval = window.setInterval(() => {
      setActiveStage((stage) => Math.min(stage + 1, stages.length - 1));
    }, STAGE_INTERVAL);

    return () => window.clearInterval(interval);
  }, [complete, error, loading]);

  useEffect(() => {
    if (!complete || loading || completedRef.current) return;

    completedRef.current = true;
    setActiveStage(stages.length);
    const timeout = window.setTimeout(onComplete, COMPLETION_DELAY);
    return () => window.clearTimeout(timeout);
  }, [complete, loading, onComplete]);

  useEffect(() => {
    if (loading) completedRef.current = false;
  }, [loading]);

  const isInterrupted = Boolean(error) && !loading;

  return (
    <motion.main
      className="atlas-pipeline"
      aria-labelledby="analysis-pipeline-title"
      initial={shouldReduceMotion ? false : { opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.24, ease: "easeOut" }}
    >
      <div className="atlas-pipeline__grid" aria-hidden="true" />

      <header className="atlas-pipeline__header">
        <AtlasLogo size="compact" />
        <div className="atlas-pipeline__header-status" aria-label="Analysis 01 is processing">
          <span>Analysis 01</span>
          <strong><i aria-hidden="true" /> Processing</strong>
        </div>
      </header>

      <section className="atlas-pipeline__content">
        <motion.div
          className="atlas-pipeline__core"
          initial={shouldReduceMotion ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.38, ease: "easeOut" }}
        >
          <p className="atlas-pipeline__eyebrow">ATLAS analysis pipeline</p>
          <h1 id="analysis-pipeline-title">Satellite infrastructure<br />intelligence</h1>
          <p className="atlas-pipeline__intro">Preparing terrain, road network, and resilience analysis.</p>

          <ol className="atlas-pipeline__stages" aria-label="Analysis stages">
            {stages.map((stage, index) => {
              const stageComplete = complete || index < activeStage;
              const stageActive = !complete && !isInterrupted && index === activeStage;
              return (
                <motion.li
                  key={stage}
                  className={stageComplete ? "is-complete" : stageActive ? "is-active" : ""}
                  initial={shouldReduceMotion ? false : { opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.22, delay: shouldReduceMotion ? 0 : index * 0.035 }}
                  aria-current={stageActive ? "step" : undefined}
                >
                  <span className="atlas-pipeline__marker" aria-hidden="true">{stageComplete ? <Check size={14} strokeWidth={2.5} /> : <i />}</span>
                  <span>{stage}</span>
                  {index < stages.length - 1 && <span className="atlas-pipeline__connector" aria-hidden="true"><i /></span>}
                </motion.li>
              );
            })}
          </ol>

          {isInterrupted && (
            <div className="atlas-pipeline__failure" role="alert">
              <p>Analysis interrupted</p>
              <span>ATLAS could not complete the analysis. Check the image or connection and try again.</span>
              <button type="button" onClick={onRetry}><RotateCcw size={16} aria-hidden="true" /> Try again</button>
            </div>
          )}
        </motion.div>
      </section>

      <footer className={`atlas-pipeline__telemetry ${complete ? "is-complete" : ""}`} aria-live="polite">
        <p><span aria-hidden="true" />{isInterrupted ? "Analysis interrupted" : complete ? "Analysis complete — opening intelligence workspace" : "Analyzing imagery"}</p>
        <span>Segmentation <i>→</i> Road network <i>→</i> Topology <i>→</i> Resilience</span>
      </footer>
    </motion.main>
  );
};

export default AnalysisPipeline;
