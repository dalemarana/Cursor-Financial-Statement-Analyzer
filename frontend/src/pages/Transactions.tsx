import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Search, Edit } from '@mui/icons-material'
import api from '../services/api'

interface Transaction {
  id: string
  date: string
  amount: string
  description: string | null
  transaction_type: string
  account_name: string | null
  balance: string | null
  category: string | null
  subcategory: string | null
  is_confirmed: boolean
}

const Transactions = () => {
  const [searchText, setSearchText] = useState('')

  const { data: transactions, isLoading, error, refetch } = useQuery({
    queryKey: ['transactions', searchText],
    queryFn: async () => {
      const params: any = { limit: 1000 }
      if (searchText) {
        params.search_text = searchText
      }
      const response = await api.get('/api/transactions', { params })
      return response.data as Transaction[]
    },
  })

  const formatCurrency = (amount: string) => {
    const num = parseFloat(amount)
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
    }).format(num)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Transactions
      </Typography>

      <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          placeholder="Search transactions..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          size="small"
          sx={{ flexGrow: 1, maxWidth: 400 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
        <Typography variant="body2" color="text.secondary">
          {transactions ? `${transactions.length} transaction${transactions.length !== 1 ? 's' : ''}` : ''}
        </Typography>
      </Box>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load transactions. Please try again.
        </Alert>
      )}

      {!isLoading && !error && transactions && transactions.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No transactions found. Upload a bank statement to get started.
          </Typography>
        </Paper>
      )}

      {!isLoading && !error && transactions && transactions.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Account</TableCell>
                <TableCell align="right">Amount</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Category</TableCell>
                <TableCell align="right">Balance</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow key={transaction.id} hover>
                  <TableCell>{formatDate(transaction.date)}</TableCell>
                  <TableCell>
                    {transaction.description || (
                      <Typography variant="body2" color="text.secondary" component="span">
                        No description
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {transaction.account_name || (
                      <Typography variant="body2" color="text.secondary" component="span">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Typography
                      variant="body2"
                      sx={{
                        color:
                          transaction.transaction_type === 'Paid In'
                            ? 'success.main'
                            : 'error.main',
                        fontWeight: 'medium',
                      }}
                    >
                      {transaction.transaction_type === 'Paid In' ? '+' : '-'}
                      {formatCurrency(transaction.amount)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={transaction.transaction_type}
                      size="small"
                      color={
                        transaction.transaction_type === 'Paid In'
                          ? 'success'
                          : 'error'
                      }
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {transaction.category ? (
                      <Box>
                        <Typography variant="body2">{transaction.category}</Typography>
                        {transaction.subcategory && (
                          <Typography variant="caption" color="text.secondary">
                            {transaction.subcategory}
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Uncategorized
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    {transaction.balance ? (
                      formatCurrency(transaction.balance)
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={transaction.is_confirmed ? 'Confirmed' : 'Pending'}
                      size="small"
                      color={transaction.is_confirmed ? 'success' : 'default'}
                      variant="outlined"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}

export default Transactions

