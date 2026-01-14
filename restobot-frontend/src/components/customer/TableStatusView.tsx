import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Avatar,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Paper,
  Divider
} from '@mui/material';
import {
  RestaurantOutlined as TableIcon,
  Refresh as RefreshIcon,
  AccessTime as TimeIcon,
  People as PeopleIcon,
  LocationOn as LocationIcon,
  EventAvailable as AvailableIcon,
  EventBusy as OccupiedIcon,
  Event as ReservedIcon
} from '@mui/icons-material';
import { tableService } from '../../services/tableService';
import { Table } from '../../types';
import { format } from 'date-fns';
import { vi } from 'date-fns/locale';

interface TableStatusViewProps {
  onBookTable?: (tableId?: number) => void;
  showBookingButton?: boolean;
  maxTables?: number;
}

const TableStatusView: React.FC<TableStatusViewProps> = ({ 
  onBookTable, 
  showBookingButton = true,
  maxTables 
}) => {
  const [tables, setTables] = useState<Table[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    const loadTablesAsync = async () => {
      try {
        setError(null);
        const response = await tableService.getTables({ size: maxTables || 20 });
        setTables(response.data);
        setLastUpdated(new Date());
      } catch (err: any) {
        console.error('Error loading tables:', err);
        setError('Không thể tải thông tin bàn. Vui lòng thử lại.');
      } finally {
        setLoading(false);
      }
    };
    
    loadTablesAsync();
    // Auto refresh every 30 seconds
    const interval = setInterval(loadTablesAsync, 30000);
    return () => clearInterval(interval);
  }, [maxTables]);

  const loadTables = async () => {
    try {
      setError(null);
      const response = await tableService.getTables({ size: maxTables || 20 });
      setTables(response.data);
      setLastUpdated(new Date());
    } catch (err: any) {
      console.error('Error loading tables:', err);
      setError('Không thể tải thông tin bàn. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    loadTables();
  };

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'available':
        return {
          label: 'Trống',
          color: 'success' as const,
          icon: <AvailableIcon />,
          description: 'Có thể đặt ngay'
        };
      case 'occupied':
        return {
          label: 'Đang sử dụng',
          color: 'warning' as const,
          icon: <OccupiedIcon />,
          description: 'Khách đang dùng bữa'
        };
      case 'reserved':
        return {
          label: 'Đã đặt',
          color: 'error' as const,
          icon: <ReservedIcon />,
          description: 'Đã có khách đặt trước'
        };
      case 'cleaning':
        return {
          label: 'Đang dọn',
          color: 'default' as const,
          icon: <TimeIcon />,
          description: 'Đang dọn dẹp, sẽ sẵn sàng sớm'
        };
      case 'maintenance':
        return {
          label: 'Bảo trì',
          color: 'default' as const,
          icon: <TimeIcon />,
          description: 'Đang bảo trì'
        };
      default:
        return {
          label: status,
          color: 'default' as const,
          icon: <TableIcon />,
          description: ''
        };
    }
  };

  const getAvailableTablesCount = () => {
    return tables.filter(table => table.current_status === 'available').length;
  };

  const getTablesByStatus = (status: string) => {
    return tables.filter(table => table.current_status === status);
  };

  if (loading && tables.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <CircularProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
          Đang tải thông tin bàn...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header with stats */}
      <Paper elevation={2} sx={{ p: 2, mb: 3, bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TableIcon />
            Trạng thái bàn nhà hàng
          </Typography>
          <Tooltip title="Làm mới">
            <IconButton 
              onClick={handleRefresh} 
              disabled={loading}
              sx={{ color: 'white' }}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {getAvailableTablesCount()}
              </Typography>
              <Typography variant="body2">Bàn trống</Typography>
            </Box>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {getTablesByStatus('occupied').length}
              </Typography>
              <Typography variant="body2">Đang sử dụng</Typography>
            </Box>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {getTablesByStatus('reserved').length}
              </Typography>
              <Typography variant="body2">Đã đặt</Typography>
            </Box>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                {tables.length}
              </Typography>
              <Typography variant="body2">Tổng bàn</Typography>
            </Box>
          </Grid>
        </Grid>

        <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', mt: 1, opacity: 0.8 }}>
          Cập nhật lần cuối: {format(lastUpdated, 'HH:mm:ss dd/MM/yyyy', { locale: vi })}
        </Typography>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Quick action button */}
      {showBookingButton && getAvailableTablesCount() > 0 && (
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => onBookTable?.()}
            sx={{ px: 4, py: 1.5 }}
          >
            Đặt bàn ngay ({getAvailableTablesCount()} bàn trống)
          </Button>
        </Box>
      )}

      {/* Tables grid */}
      <Grid container spacing={2}>
        {tables.map(table => {
          const statusInfo = getStatusInfo(table.current_status);
          
          return (
            <Grid item xs={12} sm={6} md={4} lg={3} key={table.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  border: table.current_status === 'available' ? 2 : 1,
                  borderColor: table.current_status === 'available' ? 'success.main' : 'divider',
                  '&:hover': {
                    boxShadow: 3,
                    transform: 'translateY(-2px)'
                  },
                  transition: 'all 0.2s'
                }}
              >
                <CardContent sx={{ textAlign: 'center', pb: '16px !important' }}>
                  {/* Table icon with status color */}
                  <Avatar
                    sx={{
                      bgcolor: `${statusInfo.color}.main`,
                      mx: 'auto',
                      mb: 1.5,
                      width: 56,
                      height: 56
                    }}
                  >
                    <TableIcon fontSize="large" />
                  </Avatar>

                  {/* Table number */}
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Bàn {table.table_number}
                  </Typography>

                  {/* Capacity */}
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                    <PeopleIcon fontSize="small" sx={{ mr: 0.5, opacity: 0.7 }} />
                    <Typography variant="body2">
                      {table.capacity} người
                    </Typography>
                  </Box>

                  {/* Location */}
                  {table.location && (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1.5 }}>
                      <LocationIcon fontSize="small" sx={{ mr: 0.5, opacity: 0.7 }} />
                      <Typography variant="body2" color="textSecondary">
                        {table.location}
                      </Typography>
                    </Box>
                  )}

                  {/* Status */}
                  <Chip
                    icon={statusInfo.icon}
                    label={statusInfo.label}
                    color={statusInfo.color}
                    size="small"
                    sx={{ mb: 1 }}
                  />

                  <Typography variant="caption" display="block" color="textSecondary">
                    {statusInfo.description}
                  </Typography>

                  {/* Action button for available tables */}
                  {table.current_status === 'available' && onBookTable && (
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => onBookTable(table.id)}
                      sx={{ mt: 1, width: '100%' }}
                    >
                      Đặt bàn này
                    </Button>
                  )}
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {tables.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="textSecondary">
            Không có thông tin bàn nào.
          </Typography>
        </Box>
      )}

      <Divider sx={{ my: 3 }} />

      {/* Legend */}
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Chú thích:
        </Typography>
        <Grid container spacing={1}>
          {[
            { status: 'available', label: 'Trống - Có thể đặt ngay' },
            { status: 'occupied', label: 'Đang sử dụng - Khách đang dùng bữa' },
            { status: 'reserved', label: 'Đã đặt - Có khách đặt trước' },
            { status: 'cleaning', label: 'Đang dọn - Sẽ sẵn sàng sớm' }
          ].map(({ status, label }) => {
            const statusInfo = getStatusInfo(status);
            return (
              <Grid item xs={12} sm={6} key={status}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={statusInfo.icon}
                    label={statusInfo.label}
                    color={statusInfo.color}
                    size="small"
                  />
                  <Typography variant="caption" color="textSecondary">
                    {label.split(' - ')[1]}
                  </Typography>
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    </Box>
  );
};

export default TableStatusView;