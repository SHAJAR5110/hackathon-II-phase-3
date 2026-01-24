"use client";

import { useState, useEffect } from "react";
import { X, MessageCircle } from "lucide-react";
import ChatBot from "./ChatBot";
import ChatBotErrorBoundary from "./ChatBotErrorBoundary";
import { useAuth } from "@/lib/auth-context";

/**
 * ChatBotPopup Component - Floating chat interface on dashboard
 *
 * Features:
 * - Floating button in bottom-right corner
 * - Expandable chat popup (420x600px)
 * - Responsive backdrop overlay
 * - Conversation persistence via localStorage
 * - Error handling and graceful degradation
 */
interface ChatBotPopupProps {
  onTasksModified?: () => void; // Callback when tasks are modified via chat
}

export default function ChatBotPopup({ onTasksModified }: ChatBotPopupProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const { user } = useAuth();

  // Load last conversation ID from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("lastConversationId");
    if (saved) {
      setConversationId(parseInt(saved, 10));
    }
  }, []);

  if (!user?.id) {
    return null; // Don't render if user is not authenticated
  }

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-[999] transition-opacity"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-[1000] w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        <MessageCircle className="w-7 h-7" />
      </button>

      {/* Chat Popup */}
      {isOpen && (
        <div className="fixed bottom-28 right-6 z-[1000] w-96 h-[600px] rounded-lg shadow-2xl bg-white flex flex-col overflow-hidden animate-slideUp">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-4 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Task Assistant</h3>
              <p className="text-xs text-blue-100">Powered by AI</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-blue-700 p-1 rounded transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Chat Content */}
          <ChatBotErrorBoundary>
            <ChatBot
              userId={user.id}
              conversationId={conversationId}
              onConversationIdChange={(id) => {
                setConversationId(id);
              }}
              onTasksModified={onTasksModified}
            />
          </ChatBotErrorBoundary>
        </div>
      )}

      {/* Slide-up animation keyframes */}
      <style>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }
      `}</style>
    </>
  );
}
