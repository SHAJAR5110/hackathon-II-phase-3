"use client";

import { useEffect, useRef, useCallback, useState } from "react";

interface ChatBotProps {
  userId: string;
  conversationId?: number | null;
  onConversationIdChange?: (id: number) => void;
  onTasksModified?: () => void; // Callback when tasks are modified
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ToolCall {
  tool: string;
  params: Record<string, unknown>;
}

interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

/**
 * ChatBot Component - Wrapper for OpenAI ChatKit integration
 *
 * This component provides the conversational interface for todo management.
 * It handles:
 * - Message sending to backend API
 * - Conversation history management
 * - Tool call visualization
 * - Error handling and user feedback
 */
export default function ChatBot({
  userId,
  conversationId,
  onConversationIdChange,
  onTasksModified,
}: ChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<
    number | null
  >(conversationId || null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load conversation history on mount or when conversation ID changes
  useEffect(() => {
    if (currentConversationId) {
      loadConversationHistory();
    }
  }, [currentConversationId]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /**
   * Load conversation history from localStorage or API
   */
  const loadConversationHistory = useCallback(async () => {
    try {
      // For MVP, we'll reconstruct history from state
      // In future phases, this could fetch from a GET /api/{user_id}/conversations/{conversation_id} endpoint
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load conversation history",
      );
    }
  }, [currentConversationId]);

  /**
   * Send message to backend chat endpoint
   */
  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim()) return;

      try {
        setError(null);
        setIsLoading(true);

        // Add user message to UI immediately for responsiveness
        const userMessage: Message = { role: "user", content: message };
        setMessages((prev) => [...prev, userMessage]);
        setInputValue("");

        // Send to backend
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/api/${userId}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getAuthToken()}`,
          },
          body: JSON.stringify({
            conversation_id: currentConversationId,
            message: message.trim(),
          }),
        });

        if (!response.ok) {
          const errorData = (await response
            .json()
            .catch(() => ({ detail: "" }))) as {
            detail?: string;
            error?: string;
          };
          const errorMessage =
            errorData.detail ||
            errorData.error ||
            `Failed to send message (${response.status})`;
          throw new Error(errorMessage);
        }

        const data: ChatResponse = await response.json();

        // Update conversation ID if it's a new conversation
        if (!currentConversationId) {
          setCurrentConversationId(data.conversation_id);
          onConversationIdChange?.(data.conversation_id);
        }

        // Add assistant message - strip JSON tool calls block
        const cleanResponse = stripToolCalls(data.response);
        const assistantMessage: Message = {
          role: "assistant",
          content: cleanResponse,
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Store conversation ID in localStorage for persistence
        if (data.conversation_id) {
          localStorage.setItem(
            "lastConversationId",
            data.conversation_id.toString(),
          );
        }

        // Detect if any task-modifying tools were called
        const taskModifyingTools = [
          "add_task",
          "delete_task",
          "update_task",
          "complete_task",
        ];
        const wasTaskModified = data.tool_calls?.some((call) =>
          taskModifyingTools.includes(call.tool),
        );

        // Notify parent component if tasks were modified
        if (wasTaskModified && onTasksModified) {
          // Small delay to ensure backend has processed the operation
          setTimeout(() => {
            onTasksModified();
          }, 500);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
        // Remove the user message if API call failed
        setMessages((prev) => prev.slice(0, -1));
      } finally {
        setIsLoading(false);
        inputRef.current?.focus();
      }
    },
    [userId, currentConversationId, onConversationIdChange, onTasksModified],
  );

  /**
   * Get authentication token from auth context or localStorage
   */
  const getAuthToken = (): string => {
    // First try to get from localStorage (where it's stored after login)
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth-token");
      if (token) {
        return token;
      }
    }
    // Fallback to empty string - API will reject without token
    return "";
  };

  /**
   * Strip <TOOL_CALLS> JSON blocks from response to hide implementation details
   */
  const stripToolCalls = (response: string): string => {
    // Remove both uppercase and lowercase variants
    return response
      .replace(/<TOOL_CALLS>[\s\S]*?<\/TOOL_CALLS>/gi, "")
      .trim();
  };

  /**
   * Handle Enter key press
   */
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-gray-400 mb-4">
              <svg
                className="w-16 h-16 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              Hi! I'm your task management assistant.
            </p>
            <p className="text-xs text-gray-500">
              Try: "Add a task to buy groceries" or "Show me my tasks"
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-500 text-white rounded-br-none"
                  : "bg-gray-100 text-gray-900 rounded-bl-none"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap break-words">
                {msg.content}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg rounded-bl-none">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            onClick={() => sendMessage(inputValue)}
            disabled={isLoading || !inputValue.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
