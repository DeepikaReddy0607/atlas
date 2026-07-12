import Brand from "./Brand";
import WorkspaceTabs from "./WorkspaceTabs";
import SearchBar from "./SearchBar";
import HeaderActions from "./HeaderActions";

const Header = () => {
  return (
    <header
      className="
        flex
        h-[var(--header-height)]
        items-center
        border-b
        border-[var(--atlas-border)]
        bg-[var(--atlas-bg)]
        px-6
      "
    >
      {/* Left */}
      <div className="flex items-center gap-10">
        <Brand />
        <WorkspaceTabs />
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right */}
      <div className="flex items-center gap-4">
        <SearchBar />
        <HeaderActions />
      </div>
    </header>
  );
};

export default Header;