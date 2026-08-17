import AppShell from "./components/layout/AppShell";
import { Toaster } from "sonner";
import { LayerProvider } from "./context/LayerContext";

function App() {
  return( 
  <>
  <LayerProvider>
    <AppShell />
  </LayerProvider>
    <Toaster 
      richColors 
      position="bottom-right" 
      expand = {false} />
  </>
  );
}

export default App;