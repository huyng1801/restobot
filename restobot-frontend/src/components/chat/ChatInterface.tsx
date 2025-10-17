import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Button,
  useTheme,
  Divider,
  AppBar,
  Toolbar,
  Card,
  CardContent,
  Stack,
  CircularProgress,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Restaurant as RestaurantIcon,
  TableRestaurant as TableIcon,
  MenuBook as MenuIcon,
  Info as InfoIcon,
  ShoppingCart as CartIcon,
  Circle as StatusIcon,
  Login as LoginIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { chatService } from '../../services/chatService';
import { useAuth } from '../../hooks/useAuth';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface ConnectionStatus {
  rasa: boolean;
  fastApi: boolean;
  message: string;
}

const quickButtons = [
  { icon: <TableIcon />, text: 'Đặt bàn 4 người', action: 'Đặt bàn 4 người ngày 17/10/2025 lúc 19:00' },
  { icon: <MenuIcon />, text: 'Xem thực đơn', action: 'Cho tôi xem thực đơn' },
  { icon: <CartIcon />, text: 'Gọi món', action: 'Tôi muốn gọi món ăn' },
  { icon: <InfoIcon />, text: 'Thông tin nhà hàng', action: 'Cho tôi biết thông tin về nhà hàng' },
];

// Gợi ý tin nhắn dựa trên NLU
const messageSuggestions = [
  // Greeting & Basics
  { category: '👋 Chào hỏi', text: 'Xin chào', color: '#4CAF50' },
  { category: '👋 Chào hỏi', text: 'Bạn có thể giúp tôi không', color: '#4CAF50' },
  
  // Menu & Dishes
  { category: '🍽️ Thực đơn', text: 'Cho tôi xem thực đơn', color: '#FF9800' },
  { category: '🍽️ Thực đơn', text: 'Có những món gì', color: '#FF9800' },
  { category: '🍽️ Thực đơn', text: 'Món nổi bật', color: '#FF9800' },
  { category: '🍽️ Thực đơn', text: 'Bạn recommend cái gì', color: '#FF9800' },
  { category: '🍽️ Thực đơn', text: 'Món nào được ưa chuộng', color: '#FF9800' },
  { category: '🍽️ Thực đơn', text: 'Món đặc biệt', color: '#FF9800' },
  { category: '🍽️ Thực đơn', text: 'Signature dish', color: '#FF9800' },
  
  // Booking
  { category: '🪑 Đặt bàn', text: 'Tôi muốn đặt bàn', color: '#2196F3' },
  { category: '🪑 Đặt bàn', text: 'Đặt bàn 4 người', color: '#2196F3' },
  { category: '🪑 Đặt bàn', text: 'Có bàn trống không', color: '#2196F3' },
  { category: '🪑 Đặt bàn', text: 'Đặt bàn tối nay 19:30', color: '#2196F3' },
  { category: '🪑 Đặt bàn', text: 'Đặt bàn cho gia đình', color: '#2196F3' },
  { category: '🪑 Đặt bàn', text: 'Hủy đặt bàn', color: '#2196F3' },
  
  // Ordering
  { category: '🛒 Gọi món', text: 'Tôi muốn gọi món', color: '#9C27B0' },
  { category: '🛒 Gọi món', text: 'Gọi đồ ăn', color: '#9C27B0' },
  { category: '🛒 Gọi món', text: 'Xem đơn hàng', color: '#9C27B0' },
  { category: '🛒 Gọi món', text: 'Xác nhận đơn hàng', color: '#9C27B0' },
  { category: '🛒 Gọi món', text: 'Thêm món vào đơn', color: '#9C27B0' },
  { category: '🛒 Gọi món', text: 'Sửa đơn hàng', color: '#9C27B0' },
  
  // Restaurant Info
  { category: 'ℹ️ Thông tin', text: 'Giờ mở cửa', color: '#607D8B' },
  { category: 'ℹ️ Thông tin', text: 'Địa chỉ nhà hàng', color: '#607D8B' },
  { category: 'ℹ️ Thông tin', text: 'Số điện thoại', color: '#607D8B' },
  { category: 'ℹ️ Thông tin', text: 'Có khuyến mãi gì không', color: '#607D8B' },
  { category: 'ℹ️ Thông tin', text: 'Thông tin liên hệ', color: '#607D8B' },
  
  // Popular dishes examples
  { category: '🍜 Món ăn', text: 'Tôi muốn ăn phở bò', color: '#E91E63' },
  { category: '🍜 Món ăn', text: 'Cho tôi 2 phần bò bít tết', color: '#E91E63' },
  { category: '🍜 Món ăn', text: 'Gọi 1 ly cà phê', color: '#E91E63' },
  { category: '🍜 Món ăn', text: 'Thêm cá hồi nướng', color: '#E91E63' },
  { category: '🍜 Món ăn', text: 'Giá món này bao nhiêu', color: '#E91E63' },
  
  // Confirmations
  { category: '✅ Xác nhận', text: 'Có, tôi đồng ý', color: '#4CAF50' },
  { category: '✅ Xác nhận', text: 'Được rồi', color: '#4CAF50' },
  { category: '✅ Xác nhận', text: 'Xác nhận', color: '#4CAF50' },
  { category: '❌ Từ chối', text: 'Không, cảm ơn', color: '#F44336' },
  { category: '❌ Từ chối', text: 'Hủy bỏ', color: '#F44336' },
  { category: '👋 Tạm biệt', text: 'Cảm ơn bạn', color: '#9E9E9E' },
  { category: '👋 Tạm biệt', text: 'Tạm biệt', color: '#9E9E9E' },
];

const formatMessage = (text: string): string => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
};

const ChatInterface: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [shuffledSuggestions, setShuffledSuggestions] = useState(messageSuggestions);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    rasa: false,
    fastApi: false,
    message: '🔗 Đang kiểm tra kết nối...'
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Shuffle suggestions on component mount
  useEffect(() => {
    const shuffled = [...messageSuggestions].sort(() => Math.random() - 0.5);
    setShuffledSuggestions(shuffled);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Thêm tin nhắn chào mừng
    const welcomeMessage: Message = {
      id: Date.now().toString(),
      text: `Xin chào! Tôi là RestoBot - trợ lý ảo nhà hàng.

Tôi có thể giúp bạn:
• Đặt bàn - Format: "Đặt bàn [số người] người ngày [dd/mm/yyyy] lúc [hh:mm]"
• Xem thực đơn và gợi ý món ăn
• Gọi món ăn và quản lý đơn hàng
• Thông tin nhà hàng (địa chỉ, giờ mở cửa, liên hệ)

Ví dụ đặt bàn: "Đặt bàn 4 người ngày 17/10/2025 lúc 19:00"

Bạn có thể sử dụng các nút bên dưới hoặc nhập trực tiếp!`,
      sender: 'bot',
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);

    // Kiểm tra kết nối
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const status = await chatService.getConnectionStatus();
      setConnectionStatus(status);
    } catch (error) {
      setConnectionStatus({
        rasa: false,
        fastApi: false,
        message: '❌ Lỗi khi kiểm tra kết nối'
      });
    }
  };

  const sendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim();
    if (!messageText) return;

    // Kiểm tra đăng nhập trước khi gửi
    if (!user) {
      const loginMessage: Message = {
        id: Date.now().toString(),
        text: '🔒 Bạn cần đăng nhập để sử dụng chatbot!\n\nVui lòng đăng nhập trước khi tiếp tục.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, loginMessage]);
      return;
    }

    // Thêm tin nhắn người dùng
    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      console.log('Sending message:', messageText);
      console.log('User info:', user);
      
      // Gửi message cùng với thông tin user
      const response = await chatService.sendMessage(messageText, {
        user_id: user?.id,
        username: user?.username,
        full_name: user?.full_name,
        email: user?.email,
        phone: user?.phone
      });
      console.log('Chat response:', response);
      
      // Thêm phản hồi từ bot
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: error instanceof Error ? error.message : 'Có lỗi xảy ra. Vui lòng thử lại.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  const handleSuggestionClick = (suggestionText: string) => {
    sendMessage(suggestionText);
  };

  const ConnectionIndicator = () => (
    <Chip
      icon={<StatusIcon sx={{ fontSize: 12 }} />}
      label={connectionStatus.message}
      color={connectionStatus.rasa || connectionStatus.fastApi ? 'success' : 'error'}
      size="small"
      variant="outlined"
    />
  );

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      {/* Header */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <RestaurantIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            RestoBot - Trợ lý nhà hàng
          </Typography>
          <ConnectionIndicator />
        </Toolbar>
      </AppBar>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          p: 2,
          gap: 2,
        }}
      >
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            pr: 1,
            '&::-webkit-scrollbar': {
              width: '6px',
            },
            '&::-webkit-scrollbar-track': {
              background: theme.palette.grey[100],
              borderRadius: '3px',
            },
            '&::-webkit-scrollbar-thumb': {
              background: theme.palette.grey[400],
              borderRadius: '3px',
            },
          }}
        >
          <Stack spacing={2}>
            {messages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  gap: 1,
                }}
              >
                {message.sender === 'bot' && (
                  <Avatar
                    sx={{
                      bgcolor: theme.palette.primary.main,
                      width: 36,
                      height: 36,
                    }}
                  >
                    <BotIcon fontSize="small" />
                  </Avatar>
                )}
                
                <Card
                  elevation={message.sender === 'user' ? 3 : 1}
                  sx={{
                    maxWidth: '70%',
                    bgcolor: message.sender === 'user' 
                      ? theme.palette.primary.main 
                      : theme.palette.background.paper,
                    color: message.sender === 'user' 
                      ? theme.palette.primary.contrastText 
                      : 'inherit',
                  }}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Typography
                      variant="body2"
                      sx={{ 
                        lineHeight: 1.5,
                        whiteSpace: 'pre-line',
                      }}
                      dangerouslySetInnerHTML={{
                        __html: formatMessage(message.text)
                      }}
                    />
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        mt: 1,
                        opacity: 0.7,
                        fontSize: '0.7rem',
                      }}
                    >
                      {message.timestamp.toLocaleTimeString('vi-VN', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </Typography>
                  </CardContent>
                </Card>

                {message.sender === 'user' && (
                  <Avatar
                    sx={{
                      bgcolor: theme.palette.secondary.main,
                      width: 36,
                      height: 36,
                    }}
                  >
                    <PersonIcon fontSize="small" />
                  </Avatar>
                )}
              </Box>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar
                  sx={{
                    bgcolor: theme.palette.primary.main,
                    width: 36,
                    height: 36,
                  }}
                >
                  <BotIcon fontSize="small" />
                </Avatar>
                <Card elevation={1}>
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} />
                      <Typography variant="body2" color="text.secondary">
                        Đang trả lời...
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Stack>
        </Box>

        <Divider />

        {/* Message Suggestions */}
        <Box
          sx={{
            p: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
            position: 'relative',
          }}
        >
          <Typography 
            variant="body2" 
            sx={{ 
              mb: 1.5, 
              fontWeight: 600, 
              color: 'text.primary',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            💡 Gợi ý tin nhắn nhanh:
            <Typography 
              variant="caption" 
              sx={{ 
                color: 'text.secondary',
                fontStyle: 'italic',
                ml: 'auto'
              }}
            >
              Click để gửi
            </Typography>
          </Typography>
          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 1,
              maxHeight: '140px',
              overflowY: 'auto',
              '&::-webkit-scrollbar': {
                width: '4px',
              },
              '&::-webkit-scrollbar-track': {
                background: theme.palette.grey[100],
                borderRadius: '2px',
              },
              '&::-webkit-scrollbar-thumb': {
                background: theme.palette.grey[300],
                borderRadius: '2px',
                '&:hover': {
                  background: theme.palette.grey[400],
                },
              },
            }}
          >
            {shuffledSuggestions.map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion.text}
                onClick={() => handleSuggestionClick(suggestion.text)}
                size="small"
                sx={{
                  cursor: 'pointer',
                  bgcolor: suggestion.color + '10',
                  color: suggestion.color,
                  border: `1px solid ${suggestion.color}40`,
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  borderRadius: '16px',
                  '&:hover': {
                    bgcolor: suggestion.color + '20',
                    transform: 'translateY(-1px)',
                    boxShadow: `0 2px 8px ${suggestion.color}30`,
                    borderColor: suggestion.color + '60',
                  },
                  '&:active': {
                    transform: 'translateY(0px)',
                    boxShadow: `0 1px 4px ${suggestion.color}20`,
                  },
                  transition: 'all 0.15s cubic-bezier(0.4, 0, 0.2, 1)',
                }}
              />
            ))}
          </Box>
        </Box>

        {/* Input Area */}
        <Paper
          component="form"
          onSubmit={handleSubmit}
          elevation={2}
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'flex-end',
            gap: 1,
          }}
        >
          <TextField
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Nhập tin nhắn của bạn..."
            variant="outlined"
            multiline
            maxRows={4}
            fullWidth
            size="small"
            disabled={isTyping}
            sx={{
              '& .MuiOutlinedInput-root': {
                minHeight: '40px',
              },
            }}
          />
          <IconButton
            type="submit"
            color="primary"
            disabled={!inputValue.trim() || isTyping}
            sx={{
              bgcolor: theme.palette.primary.main,
              color: 'white',
              '&:hover': {
                bgcolor: theme.palette.primary.dark,
              },
              '&:disabled': {
                bgcolor: theme.palette.grey[300],
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatInterface;