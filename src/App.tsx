import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { getToken, onMessage } from "firebase/messaging";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { messaging } from "./firebase";
import { isMobile } from "./lib/utils";
import Index from "./pages/Index";
import MobileAlertPage from "./pages/MobileAlertPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

function App() {
  useEffect(() => {
    // Request permission and get token
    Notification.requestPermission().then((permission) => {
      if (permission === "granted") {
        getToken(messaging, { vapidKey: "C4ZNkCk-Jlb5Bwf1xnb8IstC5iVkvd_om63JOCLRAt8" })
          .then((currentToken) => {
            if (currentToken) {
              console.log("FCM Token:", currentToken);
              // TODO: Send this token to your backend to store for notifications
            } else {
              console.log("No registration token available.");
            }
          })
          .catch((err) => {
            console.log("An error occurred while retrieving token. ", err);
          });
      }
    });

    // Listen for foreground messages
    onMessage(messaging, (payload) => {
      console.log('Message received. ', payload);
      // Optionally show a notification in your UI
    });
  }, []);

  if (isMobile()) {
    return <MobileAlertPage />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
