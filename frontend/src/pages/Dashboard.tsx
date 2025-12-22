import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Typography,
  Box,
  Paper,
  Button,
  Alert,
  CircularProgress,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  FormLabel,
} from '@mui/material'
import { CloudUpload, Description, ArrowForward } from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import api from '../services/api'

const Dashboard = () => {
  const navigate = useNavigate()
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadedStatementId, setUploadedStatementId] = useState<string | null>(null)
  const [accountType, setAccountType] = useState<'credit_card' | 'debit_card'>('debit_card')

  // Fetch statements to check if user has data
  const { data: statements, refetch } = useQuery({
    queryKey: ['statements'],
    queryFn: async () => {
      const response = await api.get('/api/statements')
      return response.data
    },
  })

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploading(true)
    setUploadError(null)
    setUploadSuccess(false)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('account_type', accountType)

      const response = await api.post('/api/statements/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadSuccess(true)
      setUploadedStatementId(response.data.id)
      refetch() // Refresh statements list
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        setUploadSuccess(false)
        setUploadedStatementId(null)
      }, 5000)
    } catch (error: any) {
      setUploadError(
        error.response?.data?.detail || 'Failed to upload statement'
      )
    } finally {
      setUploading(false)
    }
  }, [refetch])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  const hasData = statements && statements.length > 0

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      {!hasData ? (
        // No data - show upload prompt
        <Paper
          elevation={3}
          sx={{
            p: 4,
            mt: 3,
            textAlign: 'center',
            border: '2px dashed',
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          }}
        >
          <Description sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Get Started
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Upload your first bank statement to begin analyzing your finances
          </Typography>

          <FormControl component="fieldset" sx={{ mb: 3, width: '100%', maxWidth: 400 }}>
            <FormLabel component="legend">Account Type</FormLabel>
            <RadioGroup
              row
              value={accountType}
              onChange={(e) => setAccountType(e.target.value as 'credit_card' | 'debit_card')}
              sx={{ justifyContent: 'center' }}
            >
              <FormControlLabel
                value="debit_card"
                control={<Radio />}
                label="Debit Card"
              />
              <FormControlLabel
                value="credit_card"
                control={<Radio />}
                label="Credit Card"
              />
            </RadioGroup>
          </FormControl>

          <Box
            {...getRootProps()}
            sx={{
              p: 4,
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              backgroundColor: isDragActive ? 'action.selected' : 'background.paper',
              cursor: uploading ? 'wait' : 'pointer',
              transition: 'all 0.2s',
              '&:hover': {
                borderColor: 'primary.main',
                backgroundColor: 'action.hover',
              },
            }}
          >
            <input {...getInputProps()} />
            {uploading ? (
              <Box>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography>Uploading...</Typography>
              </Box>
            ) : (
              <Box>
                <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive
                    ? 'Drop your PDF here'
                    : 'Drag & drop a PDF statement here'}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  or click to browse
                </Typography>
                <Button variant="contained" startIcon={<CloudUpload />}>
                  Choose File
                </Button>
              </Box>
            )}
          </Box>

          {uploadError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {uploadError}
            </Alert>
          )}

          {uploadSuccess && (
            <Alert 
              severity="success" 
              sx={{ mt: 2 }}
              action={
                <Button
                  color="inherit"
                  size="small"
                  endIcon={<ArrowForward />}
                  onClick={() => navigate('/transactions')}
                >
                  View Transactions
                </Button>
              }
            >
              Statement uploaded successfully! Processing...
            </Alert>
          )}
        </Paper>
      ) : (
        // Has data - show summary and upload option
        <Box sx={{ mt: 3 }}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Your Statements
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              You have {statements.length} statement{statements.length !== 1 ? 's' : ''} uploaded
            </Typography>
            <FormControl component="fieldset" sx={{ mb: 2 }}>
              <FormLabel component="legend">Account Type</FormLabel>
              <RadioGroup
                row
                value={accountType}
                onChange={(e) => setAccountType(e.target.value as 'credit_card' | 'debit_card')}
              >
                <FormControlLabel
                  value="debit_card"
                  control={<Radio />}
                  label="Debit Card"
                />
                <FormControlLabel
                  value="credit_card"
                  control={<Radio />}
                  label="Credit Card"
                />
              </RadioGroup>
            </FormControl>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/transactions')}
              >
                View Transactions
              </Button>
              <Button
                variant="outlined"
                startIcon={<CloudUpload />}
                onClick={() => {
                  const input = document.createElement('input')
                  input.type = 'file'
                  input.accept = '.pdf'
                  input.onchange = (e: any) => {
                    if (e.target.files?.[0]) {
                      onDrop([e.target.files[0]])
                    }
                  }
                  input.click()
                }}
                disabled={uploading}
              >
                Upload Another Statement
              </Button>
            </Box>
          </Paper>

          {uploadError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {uploadError}
            </Alert>
          )}

          {uploadSuccess && (
            <Alert 
              severity="success" 
              sx={{ mb: 2 }}
              action={
                <Button
                  color="inherit"
                  size="small"
                  endIcon={<ArrowForward />}
                  onClick={() => navigate('/transactions')}
                >
                  View Transactions
                </Button>
              }
            >
              Statement uploaded successfully!
            </Alert>
          )}
        </Box>
      )}
    </Box>
  )
}

export default Dashboard

