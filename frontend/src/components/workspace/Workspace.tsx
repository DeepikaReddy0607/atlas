import { useState } from "react";

import UploadZone from "../upload/UploadZone";
import ImageViewer from "./ImageViewer";

const Workspace = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  return (
    <main
      className="
        flex-1
        overflow-hidden
        bg-[var(--atlas-bg)]
      "
    >
      {selectedFile ? (
        <ImageViewer file={selectedFile} />
      ) : (
        <div className="h-full p-8">
          <UploadZone
            onFileSelected={setSelectedFile}
          />
        </div>
      )}
    </main>
  );
};

export default Workspace;