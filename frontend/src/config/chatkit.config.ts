/**
 * ChatKit Configuration
 *
 * Centralized configuration for OpenAI ChatKit integration
 * Handles:
 * - API endpoint configuration
 * - Domain security settings
 * - Conversation persistence
 * - UI customization
 */

interface ChatKitConfig {
  api: {
    url: string;
    domainKey: string;
  };
  startScreen: {
    prompts: Array<{
      label: string;
      prompt: string;
    }>;
  };
  ui: {
    position: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
    theme: 'light' | 'dark';
  };
  persistence: {
    enabled: boolean;
    storageKey: string;
  };
}

/**
 * Get ChatKit configuration from environment variables
 * Falls back to development defaults if not set
 */
export function getChatKitConfig(): ChatKitConfig {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const domainKey =
    process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || 'localhost';

  return {
    api: {
      url: apiUrl,
      domainKey: domainKey,
    },
    startScreen: {
      prompts: [
        {
          label: 'Add a task',
          prompt:
            'Add a task to buy groceries with milk, eggs, and bread',
        },
        {
          label: 'Show tasks',
          prompt: 'Show me all my tasks',
        },
        {
          label: 'What\'s pending?',
          prompt: 'What tasks are pending?',
        },
        {
          label: 'Complete a task',
          prompt: 'Mark task 1 as complete',
        },
      ],
    },
    ui: {
      position: 'bottom-right',
      theme: 'light',
    },
    persistence: {
      enabled: true,
      storageKey: 'chatkit_conversation',
    },
  };
}

/**
 * Load conversation ID from localStorage
 * Returns null if no conversation is stored
 */
export function loadConversationId(): number | null {
  if (typeof window === 'undefined') return null;

  const config = getChatKitConfig();
  const stored = localStorage.getItem(config.persistence.storageKey);

  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      return parsed.conversationId || null;
    } catch {
      return null;
    }
  }

  return null;
}

/**
 * Save conversation ID to localStorage
 */
export function saveConversationId(conversationId: number): void {
  if (typeof window === 'undefined') return;

  const config = getChatKitConfig();
  localStorage.setItem(
    config.persistence.storageKey,
    JSON.stringify({
      conversationId,
      savedAt: new Date().toISOString(),
    })
  );
}

/**
 * Clear stored conversation (start fresh conversation)
 */
export function clearConversation(): void {
  if (typeof window === 'undefined') return;

  const config = getChatKitConfig();
  localStorage.removeItem(config.persistence.storageKey);
}

/**
 * Get API endpoint for chat
 */
export function getChatEndpoint(userId: string): string {
  const config = getChatKitConfig();
  return `${config.api.url}/api/${userId}/chat`;
}

/**
 * Validate configuration
 */
export function validateChatKitConfig(): boolean {
  const config = getChatKitConfig();

  // Check required fields
  if (!config.api.url || !config.api.domainKey) {
    console.error('ChatKit configuration missing required fields');
    return false;
  }

  // Validate URL format
  try {
    new URL(config.api.url);
  } catch {
    console.error('ChatKit API URL is invalid:', config.api.url);
    return false;
  }

  return true;
}
