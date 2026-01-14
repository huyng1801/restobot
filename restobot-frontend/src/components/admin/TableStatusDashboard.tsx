import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Box,
  Alert,
  Menu,
  MenuItem,
  IconButton
} from '@mui/material';
import {
  TableRestaurant as TableIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckInIcon,
  ExitToApp as CheckOutIcon,
  CleaningServices as CleaningIcon,
  MoreVert as MoreIcon,
  EventSeat as EventSeatIcon
} from '@mui/icons-material';
import { tableService } from '../../services';

interface Table {
  id: number;
  table_number: string;
  capacity: number;
  status: 'available' | 'occupied' | 'reserved' | 'cleaning' | 'maintenance';
  location?: string;
  is_active: boolean;
}

interface TableStatusSummary {
  available: number;
  occupied: number;
  reserved: number;
  cleaning: number;
  maintenance: number;
}

const statusColors = {
  available: 'success',
  occupied: 'error', 
  reserved: 'warning',
  cleaning: 'info',
  maintenance: 'secondary'
} as const;

const statusLabels = {
  available: 'Có sẵn',
  occupied: 'Có khách',
  reserved: 'Đã đặt',
  cleaning: 'Dọn dẹp',
  maintenance: 'Bảo trì'
} as const;

const TableStatusDashboard: React.FC = () => {
  const [tables, setTables] = useState<Table[]>([]);
  const [statusSummary, setStatusSummary] = useState<TableStatusSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<Table | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const fetchTableData = async () => {
    setLoading(true);
    try {
      const [tablesResponse, summaryResponse] = await Promise.all([
        tableService.getTables(),
        tableService.getStatusSummary()
      ]);
      
      const tablesData = Array.isArray(tablesResponse) 
        ? tablesResponse 
        : (tablesResponse?.data || []);
      
      const mappedTables = tablesData.map((t: any) => ({
        ...t,
        status: t.current_status || t.status || 'available'
      }));
      
      setTables(mappedTables);
      setStatusSummary(summaryResponse.status_summary);
      setError(null);
    } catch (err) {
      console.error('Error fetching table data:', err);
      setError('Không thể tải dữ liệu bàn');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTableData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchTableData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleTableAction = async (action: string, tableId: number) => {
    try {
      setLoading(true);
      
      switch (action) {
        case 'check-in':
          await tableService.checkIn(tableId);
          break;
        case 'check-out':
          await tableService.checkOut(tableId);
          break;
        case 'cleaning-complete':
          await tableService.completeTableCleaning(tableId);
          break;
        case 'maintenance':
          await tableService.updateTableStatus(tableId, { status: 'maintenance' });
          break;
        case 'activate':
          await tableService.updateTableStatus(tableId, { status: 'available' });
          break;
      }
      
      await fetchTableData();
      setSelectedTable(null);
    } catch (err) {
      console.error('Error performing table action:', err);
      setError('Không thể thực hiện thao tác');
    } finally {
      setLoading(false);
    }
  };

  const syncAllStatuses = async () => {
    try {
      setLoading(true);
      await tableService.syncTableStatuses();
      await fetchTableData();
      setError(null);
    } catch (err) {
      console.error('Error syncing table statuses:', err);
      setError('Không thể đồng bộ trạng thái bàn');
    } finally {
      setLoading(false);
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLButtonElement>, table: Table) => {
    setAnchorEl(event.currentTarget);
    setSelectedTable(table);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedTable(null);
  };

  const getActionMenuItems = (table: Table) => {
    const items = [];
    
    switch (table.status) {
      case 'available':
        items.push(
          { action: 'check-in', label: 'Check-in khách', icon: <CheckInIcon /> },
          { action: 'maintenance', label: 'Bảo trì', icon: <CleaningIcon /> }
        );
        break;
      case 'occupied':
        items.push(
          { action: 'check-out', label: 'Check-out khách', icon: <CheckOutIcon /> }
        );
        break;
      case 'cleaning':
        items.push(
          { action: 'cleaning-complete', label: 'Hoàn thành dọn dẹp', icon: <CheckInIcon /> }
        );
        break;
      case 'maintenance':
        items.push(
          { action: 'activate', label: 'Kích hoạt bàn', icon: <CheckInIcon /> }
        );
        break;
    }
    
    return items;
  };

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
        <Button onClick={fetchTableData} sx={{ ml: 2 }}>
          Thử lại
        </Button>
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Quản lý trạng thái bàn
        </Typography>
        <Box>
          <Button
            variant="outlined"
            onClick={syncAllStatuses}
            startIcon={<RefreshIcon />}
            disabled={loading}
            sx={{ mr: 2 }}
          >
            Đồng bộ
          </Button>
          <Button
            variant="contained"
            onClick={fetchTableData}
            startIcon={<RefreshIcon />}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Status Summary */}
      {statusSummary && (
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {Object.entries(statusSummary).map(([status, count]) => (
            <Grid item xs={12} sm={6} md={2.4} key={status}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" color={`${statusColors[status as keyof typeof statusColors]}.main`}>
                        {count}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {statusLabels[status as keyof typeof statusLabels]}
                      </Typography>
                    </Box>
                    <TableIcon sx={{ fontSize: 40, color: `${statusColors[status as keyof typeof statusColors]}.main` }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Tables Grid */}
      <Grid container spacing={3}>
        {tables.map((table) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={table.id}>
            <Card
              sx={{
                border: 2,
                borderColor: `${statusColors[table.status]}.main`,
                backgroundColor: table.status === 'available' ? 'success.light' : 
                                 table.status === 'occupied' ? 'error.light' : 'grey.50',
                '&:hover': {
                  boxShadow: 6
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <EventSeatIcon sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      Bàn {table.table_number}
                    </Typography>
                  </Box>
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuClick(e, table)}
                  >
                    <MoreIcon />
                  </IconButton>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={statusLabels[table.status]}
                    color={statusColors[table.status]}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="textSecondary">
                    Sức chứa: {table.capacity} người
                  </Typography>
                  {table.location && (
                    <Typography variant="body2" color="textSecondary">
                      Vị trí: {table.location}
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {selectedTable && getActionMenuItems(selectedTable).map((item, index) => (
          <MenuItem
            key={index}
            onClick={() => {
              handleTableAction(item.action, selectedTable.id);
              handleMenuClose();
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {item.icon}
              <Typography sx={{ ml: 1 }}>
                {item.label}
              </Typography>
            </Box>
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
};

export default TableStatusDashboard;