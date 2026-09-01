const Brand = () => {
  return (
    <div
      className="
        flex
        items-center
        gap-2
      "
    >
      <span
        className="
          font-mono
          text-[15px]
          font-semibold
          uppercase
          tracking-[0.28em]
          text-[#8BFF3D]
        "
      >
        ATLAS
      </span>

      <span
        className="
          h-[5px]
          w-[5px]
          rounded-full
          bg-[#8BFF3D]
          shadow-[0_0_8px_rgba(139,255,61,0.7)]
        "
      />
    </div>
  );
};

export default Brand;