import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import "./welcome.css";

interface WelcomeScreenProps {
  onEnterWorkspace: () => void;
}

const statuses = [
  "INITIALIZING",
  "GEOSPATIAL ENGINE",
  "TERRAIN ENGINE",
  "NETWORK ANALYSIS",
  "SYSTEM READY",
];

const nodes = [
  [8, 78],
  [21, 69],
  [33, 82],
  [69, 77],
  [82, 68],
  [93, 80],
  [15, 20],
  [86, 21],
  [6, 44],
  [96, 43],
];

const links = [
  [0, 1],
  [1, 2],
  [3, 4],
  [4, 5],
  [6, 8],
  [7, 9],
  [1, 8],
  [4, 9],
];

const WelcomeScreen = ({
  onEnterWorkspace,
}: WelcomeScreenProps) => {
  const shouldReduceMotion = useReducedMotion();

  const [statusIndex, setStatusIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  /*
   * ---------------------------------------------------------
   * SYSTEM INITIALIZATION
   * ---------------------------------------------------------
   */
  const [systemProgress, setSystemProgress] = useState(0);
const [systemReady, setSystemReady] = useState(false);

useEffect(() => {
  if (shouldReduceMotion) {
    setSystemProgress(100);
    setSystemReady(true);
    return;
  }

  setSystemProgress(0);
  setSystemReady(false);

  const duration = 4000;
  const startTime = performance.now();

  let animationFrame: number;

  const animate = (currentTime: number) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Smooth boot progression
    const eased =
      progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;

    const percentage = Math.floor(eased * 100);

    setSystemProgress(percentage);

    if (progress < 1) {
      animationFrame = requestAnimationFrame(animate);
    } else {
      setSystemProgress(100);

      // Small delay after reaching 100%
      window.setTimeout(() => {
        setSystemReady(true);
      }, 250);
    }
  };

  animationFrame = requestAnimationFrame(animate);

  return () => {
    cancelAnimationFrame(animationFrame);
  };
}, [shouldReduceMotion]);
  /*
   * ---------------------------------------------------------
   * PROGRESS
   * ---------------------------------------------------------
   */

  useEffect(() => {
    if (shouldReduceMotion) {
      setProgress(100);
      return;
    }

    let frame = 0;
    const start = performance.now();
    const duration = 2600;

    const animate = (time: number) => {
      const elapsed = time - start;
      const raw = Math.min(elapsed / duration, 1);

      const eased =
        raw < 0.5
          ? 4 * raw * raw * raw
          : 1 - Math.pow(-2 * raw + 2, 3) / 2;

      setProgress(Math.round(eased * 100));

      if (raw < 1) {
        frame = requestAnimationFrame(animate);
      }
    };

    frame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(frame);
  }, [shouldReduceMotion]);

  /*
   * ---------------------------------------------------------
   * CLOCK
   * ---------------------------------------------------------
   */

  const [clock, setClock] = useState("");

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();

      setClock(
        now.toTimeString().slice(0, 8)
      );
    };

    updateClock();

    const interval = window.setInterval(
      updateClock,
      1000
    );

    return () =>
      window.clearInterval(interval);
  }, []);

  /*
   * ---------------------------------------------------------
   * STATUS
   * ---------------------------------------------------------
   */

  const getStageClass = (threshold: number) => {
    return progress >= threshold
      ? "is-lit"
      : "";
  };

  return (
    <motion.main
      className="atlas-welcome"
      initial={
        shouldReduceMotion
          ? false
          : { opacity: 0 }
      }
      animate={{ opacity: 1 }}
      transition={{
        duration: 0.6,
        ease: "easeOut",
      }}
    >
      {/* =====================================================
          BACKGROUND
      ====================================================== */}

      <div
        className="atlas-welcome__ambient"
        aria-hidden="true"
      />

      <div
        className="atlas-welcome__grid"
        aria-hidden="true"
      />

      <svg
        className="atlas-welcome__contours"
        viewBox="0 0 1440 900"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        <path
          d="M-50 620 C200 560 350 700 600 640 S1000 520 1250 600 S1500 560 1550 600"
        />

        <path
          d="M-50 180 C250 140 400 250 650 200 S1050 120 1300 190 S1500 160 1550 190"
        />

        <path
          d="M-50 720 C220 680 420 780 680 730 S1080 660 1320 720 S1500 700 1550 720"
        />

        <path
          d="M-50 320 C260 280 460 380 700 330 S1100 260 1330 320 S1500 300 1550 320"
        />

        <path
          d="M-50 80 C230 50 430 120 690 90 S1080 40 1320 90 S1500 70 1550 90"
        />
      </svg>

      {/* =====================================================
          NETWORK FIELD
      ====================================================== */}

      <svg
        className="atlas-welcome__network"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        {links.map(([a, b], index) => {
          const start = nodes[a];
          const end = nodes[b];

          return (
            <motion.line
              key={`line-${index}`}
              x1={start[0]}
              y1={start[1]}
              x2={end[0]}
              y2={end[1]}
              className="atlas-welcome__network-line"
              initial={
                shouldReduceMotion
                  ? { opacity: 0.28 }
                  : {
                      opacity: 0,
                      pathLength: 0,
                    }
              }
              animate={{
                opacity: 0.28,
                pathLength: 1,
              }}
              transition={{
                duration: 1.2,
                delay: 1.5 + index * 0.1,
                ease: "easeOut",
              }}
            />
          );
        })}

        {nodes.map(([x, y], index) => (
          <motion.circle
            key={`node-${index}`}
            cx={x}
            cy={y}
            r="0.32"
            className="atlas-welcome__network-node"
            initial={
              shouldReduceMotion
                ? { opacity: 0.85 }
                : { opacity: 0 }
            }
            animate={{ opacity: 0.85 }}
            transition={{
              duration: 0.5,
              delay: 2.3 + index * 0.08,
            }}
          />
        ))}
      </svg>

      {/* =====================================================
          RADAR
      ====================================================== */}

      <div
        className="atlas-welcome__radar"
        aria-hidden="true"
      >
        <div className="atlas-welcome__radar-sweep" />
      </div>

      {/* =====================================================
          CORNER REGISTRATION MARKS
      ====================================================== */}

      <span className="atlas-welcome__registration atlas-welcome__registration--tl" />
      <span className="atlas-welcome__registration atlas-welcome__registration--tr" />
      <span className="atlas-welcome__registration atlas-welcome__registration--bl" />
      <span className="atlas-welcome__registration atlas-welcome__registration--br" />

      {/* =====================================================
          HEADER TELEMETRY
      ====================================================== */}

      <header className="atlas-welcome__header">
        <div>
          <div>34° 56′ 12″ N</div>
          <div>78° 14′ 45″ E</div>
        </div>

        <div className="atlas-welcome__header-right">
          <div>ATLAS / GEO-01</div>
          <div className="atlas-welcome__header-live">
            UTC {clock}
          </div>
        </div>
      </header>

      {/* =====================================================
          CORE
      ====================================================== */}

      <section className="atlas-welcome__core">

        {/* Logo construction */}

        <motion.div
          className="atlas-welcome__mark"
          initial={
            shouldReduceMotion
              ? false
              : {
                  opacity: 0,
                  scale: 0.9,
                }
          }
          animate={{
            opacity: 1,
            scale: 1,
          }}
          transition={{
            duration: 0.8,
            delay: 0.8,
            ease: [0.16, 1, 0.3, 1],
          }}
        >
          <svg
            viewBox="0 0 76 76"
            aria-hidden="true"
          >
            <line x1="10" y1="58" x2="38" y2="12" />
            <line x1="38" y1="12" x2="66" y2="58" />
            <line x1="22" y1="38" x2="52" y2="38" />
            <line x1="52" y1="38" x2="52" y2="58" />
            <rect x="49" y="55" width="6" height="6" />
          </svg>
        </motion.div>

        {/* Status */}

        <motion.div
          className="atlas-welcome__status"
          initial={
            shouldReduceMotion
              ? false
              : { opacity: 0 }
          }
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.5,
            delay: 1.25,
          }}
        >
          <span className="atlas-welcome__status-dot" />
          <span>{statuses[statusIndex]}</span>
        </motion.div>

        {/* Wordmark */}

        <div className="atlas-welcome__wordmark-wrap">
          <motion.h1
            className="atlas-welcome__wordmark"
            initial={
              shouldReduceMotion
                ? false
                : {
                    opacity: 0,
                    y: 35,
                  }
            }
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              duration: 0.9,
              delay: 1.4,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            ATLAS
          </motion.h1>
        </div>

        {/* Subtitle */}

        <motion.p
          className="atlas-welcome__subtitle"
          initial={
            shouldReduceMotion
              ? false
              : {
                  opacity: 0,
                  y: 8,
                }
          }
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.6,
            delay: 2,
          }}
        >
          AUTOMATED TERRAIN &amp; LIFELINE ANALYSIS
        </motion.p>

        <motion.div
          className="atlas-welcome__dots"
          initial={
            shouldReduceMotion
              ? false
              : { opacity: 0 }
          }
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.5,
            delay: 2.25,
          }}
        >
          <span />
          <span />
          <span className="is-active" />
        </motion.div>

        {/* Statement */}

        <div className="atlas-welcome__statement">
          <motion.div
            initial={
              shouldReduceMotion
                ? false
                : { opacity: 0, y: 10 }
            }
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: 2.35,
              duration: 0.55,
            }}
          >
            Understand the{" "}
            <strong>terrain.</strong>
          </motion.div>

          <motion.div
            initial={
              shouldReduceMotion
                ? false
                : { opacity: 0, y: 10 }
            }
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: 2.55,
              duration: 0.55,
            }}
          >
            Map the{" "}
            <strong>lifelines.</strong>
          </motion.div>

          <motion.div
            initial={
              shouldReduceMotion
                ? false
                : { opacity: 0, y: 10 }
            }
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              delay: 2.75,
              duration: 0.55,
            }}
          >
            Model the{" "}
            <strong>risk.</strong>
          </motion.div>
        </div>

        {/* Progress */}

        <motion.div
          className="atlas-welcome__progress"
          initial={
            shouldReduceMotion
              ? false
              : { opacity: 0, y: 8 }
          }
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.5,
            delay: 1.5,
            ease: "easeOut",
          }}
        >
          <div className="welcome-status">
            <div className="welcome-status__label">
              <span className={systemReady ? "is-ready" : "is-loading"} />
              {systemReady ? "SYSTEM READY" : "INITIALIZING SYSTEM"}
            </div>

            <strong>{systemProgress}%</strong>
          </div>
            <div className="welcome-progress">
              <div
                className="welcome-progress__fill"
                style={{ width: `${systemProgress}%` }}
              />
            </div>
          <div className="atlas-welcome__stages">
            <span
              className={getStageClass(10)}
            >
              GEOSPATIAL ENGINE
            </span>

            <span
              className={getStageClass(40)}
            >
              TERRAIN ENGINE
            </span>

            <span
              className={getStageClass(70)}
            >
              NETWORK ANALYSIS
            </span>

            <span
              className={getStageClass(99)}
            >
              SYSTEM READY
            </span>
          </div>
        </motion.div>

        {/* Enter */}

        <motion.div
          className="atlas-welcome__enter"
          initial={
            shouldReduceMotion
              ? false
              : {
                  opacity: 0,
                  y: 10,
                }
          }
          animate={{
            opacity: systemReady ? 1 : 0,
            y: systemReady ? 0 : 10,
          }}
          transition={{
            duration: 0.55,
            ease: "easeOut",
          }}
        >
          <button
            type="button"
            onClick={onEnterWorkspace}
            disabled={!systemReady}
            aria-label="Enter ATLAS workspace"
          >
            <span>ENTER ATLAS</span>

            <span className="atlas-welcome__arrow">
              →
            </span>
          </button>
        </motion.div>
      </section>

      {/* =====================================================
          FOOTER
      ====================================================== */}

      <footer className="atlas-welcome__footer">
        <div>
          <div>ATLAS / 01 — GEOSPATIAL ANALYSIS SYSTEM</div>
          <div>VERSION 1.8.0</div>
        </div>

        <nav>
          <span>TERRAIN</span>
          <span>NETWORKS</span>
          <span>RESILIENCE</span>
        </nav>

        <div className="atlas-welcome__footer-status">
          <i />
          {systemReady
            ? "READY FOR ANALYSIS"
            : "INITIALIZING"}
        </div>
      </footer>
    </motion.main>
  );
};

export default WelcomeScreen;