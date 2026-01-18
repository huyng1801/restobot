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
  Fab,
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
  ViewList as StatusViewIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { chatService } from '../../services/chatService';
import { useAuth } from '../../hooks/useAuth';
import TableStatusView from '../customer/TableStatusView';
import PaymentDialog from '../customer/PaymentDialog';

interface DishItem {
  name: string;
  price?: number;
  description?: string;
  image_url?: string;
  preparation_time?: number;
  category?: string;
  quantity?: number;
  unit_price?: number;
  total_price?: number;
}

interface OrderInfo {
  order_number?: string;
  total_amount?: number;
  tax_amount?: number;
  items?: DishItem[];
  status?: string;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  image?: string;
  dishes?: DishItem[];
  order?: OrderInfo;
}

interface ConnectionStatus {
  rasa: boolean;
  fastApi: boolean;
  message: string;
}

// Gợi ý tin nhắn ngắn gọn dựa trên NLU và seed data
const messageSuggestions = [
  // Chào hỏi
  { category: '👋 Chào hỏi', text: 'Xin chào', color: '#4CAF50' },
  
  // Thực đơn
  { category: '🍽️ Thực đơn', text: 'Cho tôi xem thực đơn', color: '#FF9800' },
  { category: '🍽️ Thực đơn', text: 'Món nổi bật', color: '#FF9800' },
  
  // Đặt bàn
  { category: '🪑 Đặt bàn', text: 'Đặt bàn cho 4 người', color: '#2196F3' },
  { category: '🪑 Đặt bàn', text: 'Có bàn trống không', color: '#2196F3' },
  { category: '🪑 Đặt bàn', text: 'Xem đặt bàn', color: '#2196F3' },
  
  // Gọi món
  { category: '🛒 Gọi món', text: 'Tôi muốn gọi món', color: '#9C27B0' },
  { category: '🛒 Gọi món', text: 'Xem đơn hàng', color: '#9C27B0' },
  
  // Món ăn phổ biến (từ seed data)
  { category: '🍜 Món ăn', text: 'Phở Bò Tái', color: '#E91E63' },
  { category: '🍜 Món ăn', text: 'Cơm Tấm Sườn Nướng', color: '#E91E63' },
  { category: '🍜 Món ăn', text: 'Bún Bò Huế', color: '#E91E63' },
  { category: '🍜 Món ăn', text: 'Cà Phê Sữa Đá', color: '#E91E63' },
  
  // Thanh toán
  { category: '💳 Thanh toán', text: 'Thanh toán đơn hàng', color: '#795548' },
  
  // Thông tin
  { category: 'ℹ️ Thông tin', text: 'Giờ mở cửa', color: '#607D8B' },
  { category: 'ℹ️ Thông tin', text: 'Địa chỉ nhà hàng', color: '#607D8B' },
  
  // Xác nhận/Từ chối
  { category: '✅ Xác nhận', text: 'Được rồi', color: '#4CAF50' },
  { category: '❌ Từ chối', text: 'Không, cảm ơn', color: '#F44336' },
  { category: '👋 Tạm biệt', text: 'Cảm ơn bạn', color: '#9E9E9E' },
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
  const [statusViewOpen, setStatusViewOpen] = useState(false);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [currentOrder, setCurrentOrder] = useState<any>(null);
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
• Đặt bàn - Chỉ cần nói "Tôi muốn đặt bàn" hoặc "Đặt bàn cho 4 người"
• Xem thực đơn và gợi ý món ăn
• Gọi món ăn và quản lý đơn hàng  
• Thông tin nhà hàng (địa chỉ, giờ mở cửa, liên hệ)

Bạn có thể sử dụng các nút gợi ý bên dưới hoặc nhập tin nhắn trực tiếp!`,
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

  const handleStatusView = () => {
    setStatusViewOpen(true);
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
      
      // Check for payment triggers in response
      if (response.response && (
        response.response.includes('thanh toán') ||
        response.response.includes('payment') ||
        response.response.includes('đã hoàn thành') ||
        response.response.includes('xác nhận đơn hàng')
      )) {
        // Try to extract order ID or set current order for payment
        // This could be enhanced to extract actual order data from response
        const orderIdMatch = response.response.match(/#(\d+)/);
        if (orderIdMatch) {
          setCurrentOrder({ id: orderIdMatch[1] });
        }
      }
      
      // Xử lý response từ Rasa
      if (response.dishes && response.dishes.length > 0) {
        // Nếu có danh sách món ăn, hiển thị trong một message duy nhất
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.response,
          sender: 'bot',
          timestamp: new Date(),
          dishes: response.dishes,
        };
        setMessages(prev => [...prev, botMessage]);
      } else if (response.order) {
        // Nếu có thông tin đơn hàng
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.response,
          sender: 'bot',
          timestamp: new Date(),
          order: response.order,
        };
        setMessages(prev => [...prev, botMessage]);
      } else if (Array.isArray(response.messages)) {
        // Nếu có multiple messages
        for (const msg of response.messages) {
          const botMessage: Message = {
            id: (Date.now() + Math.random()).toString(),
            text: msg.text || '',
            sender: 'bot',
            timestamp: new Date(),
            image: msg.image,
            dishes: msg.dishes,
            order: msg.order,
          };
          setMessages(prev => [...prev, botMessage]);
        }
      } else {
        // Single message response
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.response,
          sender: 'bot',
          timestamp: new Date(),
          image: response.image,
        };
        setMessages(prev => [...prev, botMessage]);
      }
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

  const AuthStatus = () => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      {user ? (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.light' }}>
            {user.username?.charAt(0).toUpperCase()}
          </Avatar>
          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'white' }}>
              {user.full_name || user.username}
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              {user.email}
            </Typography>
          </Box>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LoginIcon sx={{ color: '#ff9800' }} />
          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'white' }}>
              Chưa đăng nhập
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              Vui lòng đăng nhập để tiếp tục
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <ConnectionIndicator />
            <Divider orientation="vertical" flexItem sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
            <AuthStatus />
          </Box>
        </Toolbar>
      </AppBar>

      {/* Auth Alert */}
      {!user && (
        <Alert severity="warning" sx={{ mx: 2, mt: 2, mb: 0 }}>
          <AlertTitle>🔒 Bạn chưa đăng nhập</AlertTitle>
          Vui lòng{' '}
          <Button 
            color="warning" 
            size="small" 
            onClick={() => navigate('/login')}
            sx={{ textTransform: 'none' }}
          >
            đăng nhập
          </Button>
          {' '}hoặc{' '}
          <Button 
            color="warning" 
            size="small" 
            onClick={() => navigate('/register')}
            sx={{ textTransform: 'none' }}
          >
            đăng ký
          </Button>
          {' '}để sử dụng đầy đủ các tính năng.
        </Alert>
      )}

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
                    {message.text && (
                      <Typography
                        variant="body2"
                        sx={{ 
                          lineHeight: 1.5,
                          whiteSpace: 'pre-line',
                          mb: message.dishes ? 2 : 0,
                        }}
                        dangerouslySetInnerHTML={{
                          __html: formatMessage(message.text)
                        }}
                      />
                    )}
                    
                    {/* Hiển thị danh sách món ăn dạng card */}
                    {message.dishes && message.dishes.length > 0 && (
                      <Stack spacing={1.5} sx={{ mt: 1 }}>
                        {message.dishes.map((dish, index) => (
                          <Card 
                            key={index} 
                            variant="outlined"
                            sx={{ 
                              display: 'flex',
                              flexDirection: 'row',
                              overflow: 'hidden',
                              '&:hover': {
                                boxShadow: 2,
                              },
                            }}
                          >
                            {dish.image_url && (
                              <Box
                                sx={{
                                  width: 120,
                                  minWidth: 120,
                                  height: 100,
                                  position: 'relative',
                                  overflow: 'hidden',
                                }}
                              >
                                <img
                                  src={dish.image_url}
                                  alt={dish.name}
                                  style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                  }}
                                />
                              </Box>
                            )}
                            <CardContent sx={{ flex: 1, p: 1.5, '&:last-child': { pb: 1.5 } }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                                {dish.name}
                                {dish.quantity && (
                                  <Typography component="span" variant="body2" color="primary" sx={{ ml: 1, fontWeight: 600 }}>
                                    x{dish.quantity}
                                  </Typography>
                                )}
                              </Typography>
                              {dish.description && (
                                <Typography 
                                  variant="caption" 
                                  color="text.secondary" 
                                  sx={{ 
                                    mb: 0.5,
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    display: '-webkit-box',
                                    WebkitLineClamp: 2,
                                    WebkitBoxOrient: 'vertical',
                                  }}
                                >
                                  {dish.description}
                                </Typography>
                              )}
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                {(dish.price || dish.unit_price) && (
                                  <Chip 
                                    label={`${(dish.unit_price || dish.price)?.toLocaleString('vi-VN')}đ`}
                                    size="small"
                                    color="primary"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                )}
                                {dish.total_price && (
                                  <Chip 
                                    label={`Tổng: ${dish.total_price.toLocaleString('vi-VN')}đ`}
                                    size="small"
                                    color="secondary"
                                    sx={{ height: 20, fontSize: '0.7rem', fontWeight: 600 }}
                                  />
                                )}
                                {dish.preparation_time && (
                                  <Chip 
                                    label={`${dish.preparation_time} phút`}
                                    size="small"
                                    variant="outlined"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                )}
                                {dish.category && (
                                  <Typography variant="caption" color="text.secondary">
                                    {dish.category}
                                  </Typography>
                                )}
                              </Box>
                            </CardContent>
                          </Card>
                        ))}
                      </Stack>
                    )}
                    
                    {/* Hiển thị thông tin đơn hàng chi tiết */}
                    {message.order && (
                      <Card variant="outlined" sx={{ mt: 1, bgcolor: 'background.default' }}>
                        <CardContent sx={{ p: 2 }}>
                          {message.order.order_number && (
                            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: 'primary.main' }}>
                              📋 Đơn hàng #{message.order.order_number}
                            </Typography>
                          )}
                          
                          {message.order.items && message.order.items.length > 0 && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>
                                🍽️ Món đã gọi:
                              </Typography>
                              <Stack spacing={1}>
                                {message.order.items.map((item, index) => (
                                  <Box 
                                    key={index}
                                    sx={{ 
                                      display: 'flex', 
                                      justifyContent: 'space-between', 
                                      alignItems: 'center',
                                      p: 1.5,
                                      borderRadius: 1,
                                      bgcolor: 'grey.50',
                                      border: '1px solid',
                                      borderColor: 'grey.200'
                                    }}
                                  >
                                    <Box sx={{ flex: 1 }}>
                                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                        {item.name}
                                      </Typography>
                                      <Typography variant="caption" color="text.secondary">
                                        {(item.unit_price || item.price)?.toLocaleString('vi-VN')}đ × {item.quantity}
                                      </Typography>
                                    </Box>
                                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                                      {(item.total_price || (item.quantity! * (item.unit_price || item.price!)))?.toLocaleString('vi-VN')}đ
                                    </Typography>
                                  </Box>
                                ))}
                              </Stack>
                            </Box>
                          )}
                          
                          {(message.order.total_amount || message.order.tax_amount) && (
                            <Box sx={{ borderTop: '1px solid', borderColor: 'grey.200', pt: 2 }}>
                              {message.order.tax_amount && (
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                  <Typography variant="body2" color="text.secondary">
                                    Thuế VAT (10%):
                                  </Typography>
                                  <Typography variant="body2">
                                    {message.order.tax_amount.toLocaleString('vi-VN')}đ
                                  </Typography>
                                </Box>
                              )}
                              {message.order.total_amount && (
                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                    💰 Tổng cộng:
                                  </Typography>
                                  <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                                    {message.order.total_amount.toLocaleString('vi-VN')}đ
                                  </Typography>
                                </Box>
                              )}
                            </Box>
                          )}
                          
                          {message.order.status && (
                            <Box sx={{ mt: 2, textAlign: 'center' }}>
                              <Chip 
                                label={message.order.status}
                                color={
                                  message.order.status.includes('hoàn thành') ? 'success' :
                                  message.order.status.includes('đang') ? 'warning' : 'info'
                                }
                                sx={{ fontWeight: 600 }}
                              />
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    )}
                    
                    {/* Hiển thị single image nếu có */}
                    {message.image && !message.dishes && (
                      <Box sx={{ mb: 1 }}>
                        <img 
                          src={message.image} 
                          alt="Món ăn"
                          style={{
                            maxWidth: '100%',
                            maxHeight: '300px',
                            borderRadius: '8px',
                            objectFit: 'cover',
                          }}
                        />
                      </Box>
                    )}
                    
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

   


      {/* Table Status Dialog */}
      {statusViewOpen && (
        <Paper
          sx={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '90vw',
            maxWidth: '1200px',
            height: '80vh',
            overflow: 'auto',
            zIndex: 1300,
            p: 3,
            boxShadow: 24,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">Trạng thái bàn</Typography>
            <Button onClick={() => setStatusViewOpen(false)}>Đóng</Button>
          </Box>
          <TableStatusView 
            onBookTable={undefined}
            showBookingButton={false}
          />
        </Paper>
      )}

      {/* Backdrop for status view */}
      {statusViewOpen && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'rgba(0,0,0,0.5)',
            zIndex: 1200,
          }}
          onClick={() => setStatusViewOpen(false)}
        />
      )}

      {/* Payment Dialog */}
      <PaymentDialog
        open={paymentDialogOpen}
        onClose={() => {
          setPaymentDialogOpen(false);
          setCurrentOrder(null);
        }}
        order={currentOrder}
      />
    </Box>
  );
};

export default ChatInterface;