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
} from '@mui/icons-material';
import { chatService } from '../../services/chatService';

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

const formatMessage = (text: string): string => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
};

const ChatInterface: React.FC = () => {
  const theme = useTheme();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    rasa: false,
    fastApi: false,
    message: '🔗 Đang kiểm tra kết nối...'
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
      const response = await chatService.sendMessage(messageText);
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

            {/* Quick Buttons - chỉ hiện khi mới bắt đầu chat */}
            {messages.length === 1 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Gợi ý nhanh:
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {quickButtons.map((button, index) => (
                    <Button
                      key={index}
                      variant="outlined"
                      size="small"
                      startIcon={button.icon}
                      onClick={() => sendMessage(button.action)}
                      sx={{ mb: 1 }}
                    >
                      {button.text}
                    </Button>
                  ))}
                </Stack>
              </Box>
            )}

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