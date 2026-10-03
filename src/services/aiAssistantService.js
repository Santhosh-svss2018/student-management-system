/**
 * EduManage AI Assistant Service
 * Provides frontend API client methods to communicate with the EduAI backend chat endpoint.
 */

import { apiRequest } from './api';

export const aiAssistantService = {
  /**
   * Sends an academic query to the EduAI Assistant.
   * @param {string} message - User query or question
   * @param {string} [conversationId=null] - Optional conversation session identifier
   * @returns {Promise<{ response: string, role: string, context_used: string[], suggestions: string[], conversation_id?: string }>}
   */
  async sendMessage(message, conversationId = null) {
    if (!message || !message.trim()) {
      throw new Error('Message content cannot be empty.');
    }

    const payload = {
      message: message.trim(),
      ...(conversationId ? { conversation_id: conversationId } : {}),
    };

    return apiRequest('/api/ai-assistant/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Returns default contextual prompt suggestions based on authenticated user role.
   * @param {string} role - Authenticated user role ('student', 'teacher', or 'admin')
   * @returns {Array<{ label: string, icon?: string }>}
   */
  getDefaultSuggestions(role = 'student') {
    const roleNormalized = (role || 'student').toLowerCase();
    if (roleNormalized === 'student') {
      return [
        { label: 'What is my current attendance percentage?' },
        { label: 'What are my recent exam marks and grades?' },
        { label: 'Why is my academic risk calculated this way?' },
        { label: 'What can I do to improve my academic score?' },
      ];
    } else if (roleNormalized === 'teacher') {
      return [
        { label: 'Show me students with attendance below 75%' },
        { label: 'Which students are at high academic risk?' },
        { label: 'Summarize class academic performance' },
        { label: 'What are common risk factors in my class?' },
      ];
    } else {
      return [
        { label: 'Give me an institutional performance summary' },
        { label: 'How many students are at high risk?' },
        { label: 'Summarize attendance trends across departments' },
        { label: 'What intervention resources are recommended?' },
      ];
    }
  },
};

export default aiAssistantService;
