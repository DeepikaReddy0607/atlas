const StatusBar = () => {
  return (
    <footer
      className="
        flex
        h-[30px]
        shrink-0
        items-center
        justify-between
        border-t
        border-[#183522]
        bg-[#030B07]
        px-4
        font-mono
        text-[9px]
        uppercase
        tracking-[0.08em]
        text-[#52665A]
      "
    >

      {/* Left */}

      <div className="flex items-center gap-5">

        <span
          className="
            flex
            items-center
            gap-2
            text-[#8BFF3D]
          "
        >
          <span
            className="
              h-[5px]
              w-[5px]
              rounded-full
              bg-[#8BFF3D]
            "
          />

          Ready
        </span>

        <span>
          Project: Untitled
        </span>

      </div>


      {/* Center */}

      <div className="flex items-center gap-5">

        <span>
          Zoom 100%
        </span>

        <span>
          Coordinates -- , --
        </span>

      </div>


      {/* Right */}

      <div className="flex items-center gap-5">

        <span>
          Model: ATLAS
        </span>

        <span>
          GPU: Idle
        </span>

      </div>

    </footer>
  );
};

export default StatusBar;