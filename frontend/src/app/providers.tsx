"use client";

import { useEffect } from "react";
import { AuthProvider } from "@/lib/auth-context";

export default function Providers({ children }: { children: React.ReactNode }) {
  // Load ChatKit CDN script on client side
  useEffect(() => {
    const script = document.createElement("script");
    script.src =
      "https://cdn.platform.openai.com/deployments/chatkit/chatkit.js";
    script.async = true;
    script.addEventListener("error", () => {
      console.warn("Failed to load ChatKit CDN");
    });
    document.head.appendChild(script);

    return () => {
      // Cleanup: remove script if component unmounts
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, []);

  return <AuthProvider>{children}</AuthProvider>;
}
