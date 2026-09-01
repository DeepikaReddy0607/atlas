const NetworkBackground = () => (
  <div className="atlas-welcome__background" aria-hidden="true">
    <div className="atlas-welcome__paper" />

    <svg
      className="atlas-welcome__contours"
      viewBox="0 0 1600 1000"
      preserveAspectRatio="none"
      fill="none"
    >
      <g className="atlas-contour-group">
        <path d="M-80 210 C140 80 270 140 410 250 S690 430 850 280 S1170 70 1680 180" />
        <path d="M-100 250 C120 120 280 180 430 290 S700 470 870 320 S1190 110 1700 220" />
        <path d="M-120 295 C110 165 290 220 445 330 S720 510 895 365 S1210 155 1720 265" />

        <path d="M-80 690 C160 590 300 650 470 760 S760 930 930 780 S1250 600 1680 710" />
        <path d="M-100 730 C140 630 300 690 480 800 S770 970 950 820 S1270 640 1700 750" />
        <path d="M-120 770 C120 670 300 730 490 840 S780 1010 970 860 S1290 680 1720 790" />

        <path d="M240 -40 C300 130 230 240 340 360 S560 510 500 680 S360 900 460 1080" />
        <path d="M285 -50 C345 125 275 250 385 375 S600 525 545 695 S410 915 510 1080" />

        <path d="M1180 -50 C1090 100 1160 230 1060 360 S850 530 930 680 S1080 900 990 1080" />
        <path d="M1230 -50 C1140 105 1210 245 1110 375 S900 545 980 695 S1130 915 1040 1080" />
      </g>
    </svg>

    <div className="atlas-welcome__coordinate atlas-welcome__coordinate--top-left">
      34° 56′ 12″ N
      <span>78° 14′ 45″ E</span>
    </div>

    <div className="atlas-welcome__coordinate atlas-welcome__coordinate--top-right">
      ATLAS / GEO-01
      <span>UTC 16:12:21</span>
    </div>

    <div className="atlas-welcome__registration atlas-welcome__registration--tl" />
    <div className="atlas-welcome__registration atlas-welcome__registration--tr" />
    <div className="atlas-welcome__registration atlas-welcome__registration--bl" />
    <div className="atlas-welcome__registration atlas-welcome__registration--br" />
  </div>
);

export default NetworkBackground;