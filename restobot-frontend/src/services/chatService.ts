import { api, endpoints } from '../utils/api';

export interface ChatRequest {
  sender: string;
  message: string;
}

export interface RasaResponse {
  recipient_id: string;
  text?: string;
  image?: string;
  buttons?: Array<{
    title: string;
    payload: string;
  }>;
  custom?: any;
}

export interface ChatResponse {
  response: string;
  recipient_id?: string;
  text?: string;
}

export class ChatService {
  private rasaUrl = process.env.REACT_APP_RASA_URL || 'http://localhost:5005';
  private fastApiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  private sessionId = 'user_' + Math.random().toString(36).substr(2, 9);

  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      // Kiểm tra kết nối với Rasa trước
      const isRasaConnected = await this.checkRasaConnection();
      
      if (!isRasaConnected) {
        // Fallback to FastAPI chat endpoint if Rasa is not available
        try {
          const data = await api.post<ChatResponse>(endpoints.chat.message, {
            message,
            sender: this.sessionId
          });
          
          return {
            response: data.response || data.text || 'Xin lỗi, tôi không hiểu. Bạn có thể nói rõ hơn không?'
          };
        } catch (error) {
          throw new Error('Cả Rasa và FastAPI đều không khả dụng. Vui lòng kiểm tra server.');
        }
      }

      // Gửi tin nhắn đến Rasa webhook
      const response = await fetch(`${this.rasaUrl}/webhooks/rest/webhook`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sender: this.sessionId,
          message: message
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const rasaResponses: RasaResponse[] = await response.json();
      
      console.log('Rasa response:', rasaResponses); // Debug log
      
      if (rasaResponses && rasaResponses.length > 0) {
        // Lọc và ghép tất cả text responses
        const validResponses = rasaResponses
          .filter(r => r.text && r.text.trim().length > 0)
          .map(r => r.text!.trim());
          
        if (validResponses.length > 0) {
          return {
            response: validResponses.join('\n\n'),
            recipient_id: rasaResponses[0].recipient_id
          };
        }
      }
      
      return {
        response: 'Xin lỗi, tôi không hiểu. Bạn có thể thử hỏi cách khác không?'
      };
    } catch (error) {
      console.error('Chat service error:', error);
      throw new Error('Không thể gửi tin nhắn. Vui lòng thử lại sau.');
    }
  }

  async checkRasaConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.rasaUrl}/`, {
        method: 'GET',
        mode: 'cors'
      });
      return response.ok;
    } catch (error) {
      console.error('Rasa connection check failed:', error);
      return false;
    }
  }

  async checkFastApiConnection(): Promise<boolean> {
    try {
      await api.get('/health');
      return true;
    } catch (error) {
      console.error('FastAPI connection check failed:', error);
      return false;
    }
  }

  async getConnectionStatus(): Promise<{
    rasa: boolean;
    fastApi: boolean;
    message: string;
  }> {
    const rasaOk = await this.checkRasaConnection();
    const fastApiOk = await this.checkFastApiConnection();
    
    let message = '';
    if (rasaOk && fastApiOk) {
      message = '✅ Đã kết nối đầy đủ FastAPI + Rasa';
    } else if (fastApiOk) {
      message = '⚠️ Chỉ FastAPI hoạt động. Vui lòng khởi động Rasa: python start_rasa.py';
    } else if (rasaOk) {
      message = '⚠️ Chỉ Rasa hoạt động. Vui lòng khởi động FastAPI: python start_fastapi.py';
    } else {
      message = '❌ Không kết nối được. Vui lòng khởi động servers.';
    }
    
    return {
      rasa: rasaOk,
      fastApi: fastApiOk,
      message
    };
  }

  getSessionId(): string {
    return this.sessionId;
  }

  resetSession(): void {
    this.sessionId = 'user_' + Math.random().toString(36).substr(2, 9);
  }
}

export const chatService = new ChatService();