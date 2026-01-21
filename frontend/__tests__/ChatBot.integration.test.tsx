/**
 * ChatBot Integration Tests
 *
 * Tests for ChatBot and ChatBotPopup components
 * Covers:
 * - Component rendering
 * - Message sending/receiving
 * - Error handling
 * - Conversation persistence
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ChatBot from '@/components/ChatBot';
import ChatBotPopup from '@/components/ChatBotPopup';
import ChatBotErrorBoundary from '@/components/ChatBotErrorBoundary';

// Mock the auth context
jest.mock('@/lib/auth-context', () => ({
  useAuth: () => ({
    user: {
      id: 'testuser123',
      email: 'test@example.com',
    },
  }),
}));

// Mock fetch
global.fetch = jest.fn();

describe('ChatBot Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render chat interface with empty state', () => {
      render(<ChatBot userId="testuser123" />);

      expect(
        screen.getByText(/Hi! I'm your task management assistant/)
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText('Ask me anything...')
      ).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Send/i })).toBeInTheDocument();
    });

    it('should render with initial conversation ID', () => {
      const handleChange = jest.fn();
      render(
        <ChatBot
          userId="testuser123"
          conversationId={42}
          onConversationIdChange={handleChange}
        />
      );

      // Component should initialize with conversation ID
      expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument();
    });

    it('should have input field and send button', () => {
      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText('Ask me anything...');
      const sendButton = screen.getByRole('button', { name: /Send/i });

      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'text');
      expect(sendButton).toBeInTheDocument();
      expect(sendButton).toBeDisabled(); // Should be disabled when input is empty
    });
  });

  describe('Message Sending', () => {
    it('should send message and display user message', async () => {
      const mockResponse: any = {
        conversation_id: 1,
        response: "I've added 'Buy groceries' to your task list!",
        tool_calls: [
          {
            tool: 'add_task',
            params: {
              user_id: 'testuser123',
              title: 'Buy groceries',
            },
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText('Ask me anything...');
      const sendButton = screen.getByRole('button', { name: /Send/i });

      // Type message
      await userEvent.type(input, 'Add a task to buy groceries');

      // Send message
      fireEvent.click(sendButton);

      // Wait for user message to appear
      await waitFor(() => {
        expect(
          screen.getByText('Add a task to buy groceries')
        ).toBeInTheDocument();
      });

      // Wait for assistant response
      await waitFor(() => {
        expect(
          screen.getByText("I've added 'Buy groceries' to your task list!")
        ).toBeInTheDocument();
      });
    });

    it('should clear input after sending', async () => {
      const mockResponse: any = {
        conversation_id: 1,
        response: 'Task added!',
        tool_calls: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText(
        'Ask me anything...'
      ) as HTMLInputElement;
      const sendButton = screen.getByRole('button', { name: /Send/i });

      await userEvent.type(input, 'Test message');
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });

    it('should handle Enter key to send message', async () => {
      const mockResponse: any = {
        conversation_id: 1,
        response: 'Got it!',
        tool_calls: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText('Ask me anything...');

      await userEvent.type(input, 'Test message');
      fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

      await waitFor(() => {
        expect(screen.getByText('Test message')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error when fetch fails', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText('Ask me anything...');
      const sendButton = screen.getByRole('button', { name: /Send/i });

      await userEvent.type(input, 'Test message');
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    it('should display error on 401 unauthorized', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Unauthorized' }),
      });

      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText('Ask me anything...');
      const sendButton = screen.getByRole('button', { name: /Send/i });

      await userEvent.type(input, 'Test message');
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Unauthorized')).toBeInTheDocument();
      });
    });

    it('should remove user message if API call fails', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('API error')
      );

      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText('Ask me anything...');
      const sendButton = screen.getByRole('button', { name: /Send/i });

      await userEvent.type(input, 'Test message');
      fireEvent.click(sendButton);

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText('API error')).toBeInTheDocument();
      });

      // User message should be removed since API call failed
      expect(screen.queryByText('Test message')).not.toBeInTheDocument();
    });
  });

  describe('Conversation Management', () => {
    it('should update conversation ID when creating new conversation', async () => {
      const handleChange = jest.fn();
      const mockResponse: any = {
        conversation_id: 42,
        response: 'Got it!',
        tool_calls: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(
        <ChatBot
          userId="testuser123"
          onConversationIdChange={handleChange}
        />
      );

      const input = screen.getByPlaceholderText('Ask me anything...');
      const sendButton = screen.getByRole('button', { name: /Send/i });

      await userEvent.type(input, 'Test message');
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(handleChange).toHaveBeenCalledWith(42);
      });
    });

    it('should save conversation ID to localStorage', async () => {
      const mockResponse: any = {
        conversation_id: 42,
        response: 'Got it!',
        tool_calls: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<ChatBot userId="testuser123" />);

      const input = screen.getByPlaceholderText('Ask me anything...');
      const sendButton = screen.getByRole('button', { name: /Send/i });

      await userEvent.type(input, 'Test message');
      fireEvent.click(sendButton);

      await waitFor(() => {
        expect(localStorage.getItem('lastConversationId')).toBe('42');
      });
    });
  });
});

describe('ChatBotPopup Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render floating button', () => {
      render(<ChatBotPopup />);

      const button = screen.getByRole('button', { name: /Open chat/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('fixed', 'bottom-6', 'right-6');
    });

    it('should not render popup initially', () => {
      render(<ChatBotPopup />);

      expect(screen.queryByText('Task Assistant')).not.toBeInTheDocument();
    });

    it('should show popup when button is clicked', async () => {
      render(<ChatBotPopup />);

      const button = screen.getByRole('button', { name: /Open chat/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Task Assistant')).toBeInTheDocument();
      });
    });

    it('should close popup when close button is clicked', async () => {
      render(<ChatBotPopup />);

      const openButton = screen.getByRole('button', { name: /Open chat/i });
      fireEvent.click(openButton);

      await waitFor(() => {
        expect(screen.getByText('Task Assistant')).toBeInTheDocument();
      });

      const closeButton = screen.getByRole('button', { name: /Close chat/i });
      fireEvent.click(closeButton);

      await waitFor(() => {
        expect(screen.queryByText('Task Assistant')).not.toBeInTheDocument();
      });
    });

    it('should toggle popup on button click', async () => {
      render(<ChatBotPopup />);

      const button = screen.getByRole('button', { name: /Open chat/i });

      // Open
      fireEvent.click(button);
      await waitFor(() => {
        expect(screen.getByText('Task Assistant')).toBeInTheDocument();
      });

      // Close
      fireEvent.click(button);
      await waitFor(() => {
        expect(screen.queryByText('Task Assistant')).not.toBeInTheDocument();
      });

      // Open again
      fireEvent.click(button);
      await waitFor(() => {
        expect(screen.getByText('Task Assistant')).toBeInTheDocument();
      });
    });
  });

  describe('Integration', () => {
    it('should render ChatBot inside popup', async () => {
      render(<ChatBotPopup />);

      const button = screen.getByRole('button', { name: /Open chat/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument();
      });
    });
  });
});

describe('ChatBotErrorBoundary', () => {
  // Suppress console.error for error boundary tests
  const consoleError = jest.spyOn(console, 'error').mockImplementation();

  afterAll(() => {
    consoleError.mockRestore();
  });

  it('should render children when no error', () => {
    render(
      <ChatBotErrorBoundary>
        <div>Test content</div>
      </ChatBotErrorBoundary>
    );

    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('should render error fallback on error', () => {
    const TestComponent = () => {
      throw new Error('Test error');
    };

    render(
      <ChatBotErrorBoundary>
        <TestComponent />
      </ChatBotErrorBoundary>
    );

    expect(
      screen.getByText(/Chat temporarily unavailable/)
    ).toBeInTheDocument();
    expect(screen.getByText(/has been logged/)).toBeInTheDocument();
  });

  it('should render retry button', () => {
    const TestComponent = () => {
      throw new Error('Test error');
    };

    render(
      <ChatBotErrorBoundary>
        <TestComponent />
      </ChatBotErrorBoundary>
    );

    expect(screen.getByRole('button', { name: /Try again/i })).toBeInTheDocument();
  });

  it('should recover when retry is clicked', () => {
    let shouldThrow = true;

    const TestComponent = () => {
      if (shouldThrow) {
        throw new Error('Test error');
      }
      return <div>Recovered</div>;
    };

    const { rerender } = render(
      <ChatBotErrorBoundary>
        <TestComponent />
      </ChatBotErrorBoundary>
    );

    expect(screen.getByText(/Chat temporarily unavailable/)).toBeInTheDocument();

    shouldThrow = false;
    const retryButton = screen.getByRole('button', { name: /Try again/i });
    fireEvent.click(retryButton);

    rerender(
      <ChatBotErrorBoundary>
        <TestComponent />
      </ChatBotErrorBoundary>
    );

    expect(screen.getByText('Recovered')).toBeInTheDocument();
  });
});
