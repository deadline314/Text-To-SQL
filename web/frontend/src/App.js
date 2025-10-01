import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Divider,
  Switch,
  FormControlLabel,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Collapse,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CodeIcon from '@mui/icons-material/Code';
import SchemaIcon from '@mui/icons-material/Storage';
import HelpIcon from '@mui/icons-material/Help';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import CloseIcon from '@mui/icons-material/Close';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import PendingIcon from '@mui/icons-material/Pending';
import StopIcon from '@mui/icons-material/Stop';

const API_BASE = 'http://localhost:8001';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#64b5f6',
    },
    secondary: {
      main: '#81c784',
    },
    background: {
      default: '#0a1929',
      paper: 'rgba(26, 35, 50, 0.95)',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backdropFilter: 'blur(20px)',
        },
      },
    },
  },
});

const MotionPaper = motion(Paper);
const MotionBox = motion(Box);

function App() {
  const [tabIndex, setTabIndex] = useState(0);
  const [query, setQuery] = useState('');
  const [sql, setSql] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [provider, setProvider] = useState('local');
  const [modelId, setModelId] = useState('');
  const [schema, setSchema] = useState(null);
  const [examples, setExamples] = useState([]);
  const [expandedTable, setExpandedTable] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [queryResults, setQueryResults] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [autoMode, setAutoMode] = useState(false);
  const [autoExecuting, setAutoExecuting] = useState(false);
  const [executionHistory, setExecutionHistory] = useState([]);
  const [abortController, setAbortController] = useState(null);

  useEffect(() => {
    fetchSchema();
    fetchExamples();
  }, []);

  const fetchSchema = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/schema`);
      setSchema(response.data);
    } catch (err) {
      console.error('Failed to fetch schema:', err);
    }
  };

  const fetchExamples = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/examples`);
      setExamples(response.data.examples);
    } catch (err) {
      console.error('Failed to fetch examples:', err);
    }
  };

  const handleGenerate = async () => {
    if (!query.trim()) {
      showSnackbar('請輸入查詢語句', 'warning');
      return;
    }

    setLoading(true);
    setError('');
    setSql('');
    setQueryResults(null);

    try {
      const response = await axios.post(`${API_BASE}/api/generate`, {
        query: query.trim(),
        provider: provider,
        model_id: modelId || null,
        stream: false,
      });

      const generatedSql = response.data.cleaned_sql || response.data.sql;
      setSql(generatedSql);
      showSnackbar('SQL 生成成功！', 'success');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || '生成失敗，請重試';
      setError(errorMsg);
      showSnackbar(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!sql.trim()) {
      showSnackbar('沒有可執行的 SQL 語句', 'warning');
      return;
    }

    setExecuting(true);
    setQueryResults(null);

    try {
      const response = await axios.post(`${API_BASE}/api/execute`, {
        sql: sql.trim(),
      });

      setQueryResults(response.data);
      showSnackbar(`查詢成功！找到 ${response.data.row_count} 筆資料`, 'success');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || '執行失敗，請檢查 SQL 語法';
      showSnackbar(errorMsg, 'error');
    } finally {
      setExecuting(false);
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleAbort = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setAutoExecuting(false);
      showSnackbar('已中止自動執行', 'warning');
    }
  };

  const handleAutoExecute = async () => {
    if (!query.trim()) {
      showSnackbar('請輸入查詢語句', 'warning');
      return;
    }

    // Create new AbortController
    const controller = new AbortController();
    setAbortController(controller);

    setAutoExecuting(true);
    setExecutionHistory([]);
    setQueryResults(null);
    setSql('');

    try {
      const response = await fetch(`${API_BASE}/api/auto-execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          provider: provider,
          model_id: modelId || null,
          stream: true,
          max_retries: 5,
        }),
        signal: controller.signal,
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setAutoExecuting(false);
              return;
            }

            try {
              const event = JSON.parse(data);

              if (event.type === 'start') {
                // Initial start notification
                showSnackbar(event.message, 'info');
              } else if (event.type === 'generating') {
                // Add new attempt with generating status
                setExecutionHistory((prev) => {
                  const existingIndex = prev.findIndex(h => h.attempt === event.attempt);
                  if (existingIndex >= 0) {
                    const newHistory = [...prev];
                    newHistory[existingIndex] = {
                      attempt: event.attempt,
                      sql: null,
                      status: event.status,
                      success: null,
                      error: null,
                    };
                    return newHistory;
                  } else {
                    return [
                      ...prev,
                      {
                        attempt: event.attempt,
                        sql: null,
                        status: event.status,
                        success: null,
                        error: null,
                      },
                    ];
                  }
                });
              } else if (event.type === 'generated') {
                // Update with generated SQL
                setExecutionHistory((prev) => {
                  const newHistory = [...prev];
                  const index = newHistory.findIndex(h => h.attempt === event.attempt);
                  if (index >= 0) {
                    newHistory[index] = {
                      ...newHistory[index],
                      sql: event.sql,
                      raw_sql: event.raw_sql,  // Store raw SQL for debugging
                      status: event.status,
                    };
                  }
                  return newHistory;
                });
                // Also update the main SQL display for debugging
                setSql(event.sql);
              } else if (event.type === 'executing') {
                // Update with executing status
                setExecutionHistory((prev) => {
                  const newHistory = [...prev];
                  const index = newHistory.findIndex(h => h.attempt === event.attempt);
                  if (index >= 0) {
                    newHistory[index] = {
                      ...newHistory[index],
                      status: event.status,
                    };
                  }
                  return newHistory;
                });
              } else if (event.type === 'success') {
                // Update the attempt to success
                setExecutionHistory((prev) => {
                  const newHistory = [...prev];
                  const index = newHistory.findIndex(h => h.attempt === event.attempt);
                  if (index >= 0) {
                    newHistory[index] = {
                      attempt: event.attempt,
                      sql: event.sql,
                      status: event.status,
                      success: true,
                      error: null,
                    };
                  }
                  return newHistory;
                });
                setQueryResults(event.result);
                setSql(event.sql);
                showSnackbar(
                  `執行成功！經過 ${event.attempt} 次嘗試，找到 ${event.result.row_count} 筆資料`,
                  'success'
                );
              } else if (event.type === 'error') {
                // Update or add the failed attempt to history immediately
                setExecutionHistory((prev) => {
                  const newHistory = [...prev];
                  const existingIndex = newHistory.findIndex(h => h.attempt === event.attempt);
                  
                  const errorEntry = {
                    attempt: event.attempt,
                    sql: event.sql,
                    status: '失敗',
                    success: false,
                    error: event.error,
                    prompt: event.prompt || null,  // Include prompt if available
                  };

                  if (existingIndex >= 0) {
                    // Update existing entry
                    newHistory[existingIndex] = errorEntry;
                  } else {
                    // Add new entry if not found
                    newHistory.push(errorEntry);
                  }
                  
                  return newHistory;
                });
                
                // Show snackbar for final error only
                if (event.is_final) {
                  showSnackbar(`執行失敗：${event.error}`, 'error');
                }
              } else if (event.type === 'final_error') {
                showSnackbar(event.message, 'error');
              } else if (event.type === 'fatal_error') {
                showSnackbar(`嚴重錯誤：${event.message}`, 'error');
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        // User cancelled the request
        showSnackbar('已中止自動執行', 'warning');
      } else {
        showSnackbar('自動執行失敗：' + err.message, 'error');
      }
    } finally {
      setAutoExecuting(false);
      setAbortController(null);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    setTabIndex(0);
  };

  const handleModeChange = (event) => {
    setAutoMode(event.target.checked);
    setExecutionHistory([]);
    setQueryResults(null);
    setSql('');
  };

  const toggleTable = (tableName) => {
    setExpandedTable(expandedTable === tableName ? null : tableName);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box
        sx={{
          minHeight: '100vh',
          background: 'radial-gradient(ellipse at top, #1a2942 0%, #0a1929 50%, #000000 100%)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 20% 50%, rgba(100, 181, 246, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(129, 199, 132, 0.1) 0%, transparent 50%)',
            pointerEvents: 'none',
          },
          py: 4,
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <MotionBox
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
              <motion.img
                src="/logo.png"
                alt="Text-to-SQL Logo"
                style={{ width: 80, height: 80, marginRight: 16 }}
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ duration: 0.8, type: 'spring' }}
              />
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 700,
                  background: 'linear-gradient(135deg, #64b5f6 0%, #81c784 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: '0 0 30px rgba(100, 181, 246, 0.3)',
                }}
              >
                Text-to-SQL
              </Typography>
            </Box>
            <Typography
              variant="subtitle1"
              align="center"
              sx={{
                mb: 4,
                color: 'rgba(255, 255, 255, 0.7)',
                fontWeight: 300,
              }}
            >
              將自然語言轉換為 SQL 查詢語句
            </Typography>
          </MotionBox>

          <Paper
            elevation={0}
            sx={{
              mb: 3,
              background: 'rgba(26, 35, 50, 0.6)',
              border: '1px solid rgba(100, 181, 246, 0.2)',
            }}
          >
            <Tabs
              value={tabIndex}
              onChange={(e, v) => setTabIndex(v)}
              centered
              sx={{
                '& .MuiTab-root': {
                  color: 'rgba(255, 255, 255, 0.6)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    color: '#64b5f6',
                  },
                  '&.Mui-selected': {
                    color: '#64b5f6',
                  },
                },
                '& .MuiTabs-indicator': {
                  backgroundColor: '#64b5f6',
                  height: 3,
                  borderRadius: '3px 3px 0 0',
                },
              }}
            >
              <Tab icon={<CodeIcon />} label="SQL 生成" iconPosition="start" />
              <Tab icon={<HelpIcon />} label="使用說明" iconPosition="start" />
              <Tab icon={<SchemaIcon />} label="資料庫結構" iconPosition="start" />
            </Tabs>
          </Paper>

          <AnimatePresence mode="wait">
            {tabIndex === 0 && (
              <MotionPaper
                key="generate"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ duration: 0.3 }}
                elevation={0}
                sx={{
                  p: 4,
                  background: 'rgba(26, 35, 50, 0.8)',
                  border: '1px solid rgba(100, 181, 246, 0.2)',
                  borderRadius: 2,
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h5">
                    輸入查詢
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={autoMode}
                        onChange={handleModeChange}
                        color="primary"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AutoFixHighIcon />
                        <Typography>自動執行模式</Typography>
                      </Box>
                    }
                  />
                </Box>

                <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
                  <FormControl sx={{ minWidth: 150 }}>
                    <InputLabel>模型提供者</InputLabel>
                    <Select value={provider} onChange={(e) => setProvider(e.target.value)}>
                      <MenuItem value="local">本地模型</MenuItem>
                      <MenuItem value="bedrock">AWS Bedrock</MenuItem>
                      <MenuItem value="genai">Google GenAI</MenuItem>
                    </Select>
                  </FormControl>

                  {provider !== 'local' && (
                    <TextField
                      label="模型 ID (可選)"
                      value={modelId}
                      onChange={(e) => setModelId(e.target.value)}
                      sx={{ flex: 1 }}
                      placeholder={
                        provider === 'bedrock'
                          ? 'us.anthropic.claude-sonnet-4-20250514-v1:0'
                          : 'gemini-2.0-flash-exp'
                      }
                    />
                  )}
                </Box>

                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="例如：查詢 2024 年 1 月的所有帳單記錄"
                  sx={{ mb: 3 }}
                />

                {!autoMode ? (
                  <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={handleGenerate}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
                  sx={{
                    mb: 3,
                    py: 1.5,
                    background: 'linear-gradient(135deg, #64b5f6 0%, #81c784 100%)',
                    boxShadow: '0 4px 20px rgba(100, 181, 246, 0.4)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5ba3e0 0%, #6fb070 100%)',
                      boxShadow: '0 6px 25px rgba(100, 181, 246, 0.6)',
                      transform: 'translateY(-2px)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  {loading ? '生成中...' : '生成 SQL'}
                </Button>
                ) : (
                  <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
                    <Button
                      variant="contained"
                      size="large"
                      fullWidth
                      onClick={handleAutoExecute}
                      disabled={autoExecuting}
                      startIcon={autoExecuting ? <CircularProgress size={20} /> : <AutoFixHighIcon />}
                      sx={{
                        py: 1.5,
                        background: 'linear-gradient(135deg, #9c27b0 0%, #e91e63 100%)',
                        boxShadow: '0 4px 20px rgba(156, 39, 176, 0.4)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #8e24aa 0%, #d81b60 100%)',
                          boxShadow: '0 6px 25px rgba(156, 39, 176, 0.6)',
                          transform: 'translateY(-2px)',
                        },
                        transition: 'all 0.3s ease',
                      }}
                    >
                      {autoExecuting ? '自動執行中...' : '自動生成並執行'}
                    </Button>
                    {autoExecuting && (
                      <Button
                        variant="outlined"
                        size="large"
                        onClick={handleAbort}
                        startIcon={<StopIcon />}
                        sx={{
                          py: 1.5,
                          minWidth: '120px',
                          borderColor: '#ef5350',
                          color: '#ef5350',
                          '&:hover': {
                            borderColor: '#d32f2f',
                            backgroundColor: 'rgba(239, 83, 80, 0.1)',
                            transform: 'translateY(-2px)',
                          },
                          transition: 'all 0.3s ease',
                        }}
                      >
                        中止
                      </Button>
                    )}
                  </Box>
                )}

                {executionHistory.length > 0 && (
                  <MotionBox
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    sx={{ mb: 3 }}
                  >
                    <Typography variant="h6" gutterBottom>
                      執行歷程
                    </Typography>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 3,
                        background: 'rgba(26, 35, 50, 0.6)',
                        border: '1px solid rgba(156, 39, 176, 0.2)',
                        borderRadius: 2,
                      }}
                    >
                      <Stepper orientation="vertical" activeStep={executionHistory.length}>
                        {executionHistory.map((step, index) => (
                          <Step key={index} completed={step.success !== null}>
                            <StepLabel
                              icon={
                                step.success === null ? (
                                  <PendingIcon sx={{ color: '#ffa726' }} />
                                ) : step.success ? (
                                  <CheckCircleIcon sx={{ color: '#81c784' }} />
                                ) : (
                                  <ErrorIcon sx={{ color: '#e57373' }} />
                                )
                              }
                            >
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                <Typography
                                  sx={{
                                    color:
                                      step.success === null
                                        ? '#ffa726'
                                        : step.success
                                        ? '#81c784'
                                        : '#e57373',
                                    fontWeight: 'bold',
                                  }}
                                >
                                  第 {step.attempt} 次嘗試
                                </Typography>
                                <Chip
                                  label={step.status || (step.success === null ? '執行中' : step.success ? '成功' : '失敗')}
                                  size="small"
                                  sx={{
                                    background:
                                      step.success === null
                                        ? 'rgba(255, 167, 38, 0.2)'
                                        : step.success
                                        ? 'rgba(129, 199, 132, 0.2)'
                                        : 'rgba(229, 115, 115, 0.2)',
                                    color:
                                      step.success === null
                                        ? '#ffa726'
                                        : step.success
                                        ? '#81c784'
                                        : '#e57373',
                                    border: `1px solid ${
                                      step.success === null
                                        ? '#ffa726'
                                        : step.success
                                        ? '#81c784'
                                        : '#e57373'
                                    }`,
                                  }}
                                />
                              </Box>
                            </StepLabel>
                            <StepContent>
                              <Paper
                                sx={{
                                  p: 2,
                                  mt: 1,
                                  background: 'rgba(0, 0, 0, 0.3)',
                                  border: '1px solid rgba(255, 255, 255, 0.1)',
                                }}
                              >
                                {step.sql ? (
                                  <>
                                    <Typography
                                      variant="caption"
                                      sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1, display: 'block' }}
                                    >
                                      清理後的 SQL:
                                    </Typography>
                                    <Typography
                                      sx={{
                                        fontFamily: '"Fira Code", monospace',
                                        fontSize: '0.85rem',
                                        color: '#4ade80',
                                        mb: 2,
                                        whiteSpace: 'pre-wrap',
                                      }}
                                    >
                                      {step.sql}
                                    </Typography>
                                    {step.raw_sql && (
                                      <>
                                        <Typography
                                          variant="caption"
                                          sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1, display: 'block' }}
                                        >
                                          原始輸出（除錯用）:
                                        </Typography>
                                        <Paper
                                          sx={{
                                            p: 1.5,
                                            mb: 2,
                                            background: 'rgba(0, 0, 0, 0.5)',
                                            border: '1px solid rgba(255, 167, 38, 0.2)',
                                            maxHeight: '150px',
                                            overflow: 'auto',
                                          }}
                                        >
                                          <Typography
                                            sx={{
                                              fontFamily: '"Fira Code", monospace',
                                              fontSize: '0.75rem',
                                              color: '#ffa726',
                                              whiteSpace: 'pre-wrap',
                                              wordBreak: 'break-word',
                                            }}
                                          >
                                            {step.raw_sql}
                                          </Typography>
                                        </Paper>
                                      </>
                                    )}
                                  </>
                                ) : (
                                  <Typography
                                    sx={{
                                      color: 'rgba(255, 255, 255, 0.6)',
                                      fontSize: '0.9rem',
                                      fontStyle: 'italic',
                                    }}
                                  >
                                    {step.status || '處理中...'}
                                  </Typography>
                                )}
                                {step.error && (
                                  <>
                                    <Typography
                                      variant="caption"
                                      sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1, display: 'block' }}
                                    >
                                      錯誤訊息:
                                    </Typography>
                                    <Typography sx={{ fontSize: '0.85rem', color: '#e57373', mb: 2 }}>
                                      {step.error}
                                    </Typography>
                                  </>
                                )}
                                {step.prompt && (
                                  <>
                                    <Typography
                                      variant="caption"
                                      sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1, display: 'block' }}
                                    >
                                      實際 Prompt（點擊展開）:
                                    </Typography>
                                    <Paper
                                      sx={{
                                        p: 2,
                                        background: 'rgba(0, 0, 0, 0.5)',
                                        border: '1px solid rgba(100, 181, 246, 0.2)',
                                        maxHeight: '200px',
                                        overflow: 'auto',
                                        cursor: 'pointer',
                                        '&:hover': {
                                          borderColor: 'rgba(100, 181, 246, 0.4)',
                                        },
                                      }}
                                      onClick={(e) => {
                                        const target = e.currentTarget;
                                        target.style.maxHeight = target.style.maxHeight === '200px' ? 'none' : '200px';
                                      }}
                                    >
                                      <Typography
                                        sx={{
                                          fontFamily: '"Fira Code", monospace',
                                          fontSize: '0.75rem',
                                          color: '#64b5f6',
                                          whiteSpace: 'pre-wrap',
                                          wordBreak: 'break-word',
                                        }}
                                      >
                                        {step.prompt}
                                      </Typography>
                                    </Paper>
                                  </>
                                )}
                              </Paper>
                            </StepContent>
                          </Step>
                        ))}
                      </Stepper>
                    </Paper>
                  </MotionBox>
                )}

                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}

                {sql && (
                  <MotionBox
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6">
                        生成的 SQL
                      </Typography>
                      <Button
                        variant="contained"
                        onClick={handleExecute}
                        disabled={executing}
                        startIcon={executing ? <CircularProgress size={16} /> : <PlayCircleOutlineIcon />}
                        sx={{
                          background: 'linear-gradient(135deg, #81c784 0%, #64b5f6 100%)',
                          boxShadow: '0 4px 20px rgba(129, 199, 132, 0.4)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #6fb070 0%, #5ba3e0 100%)',
                            boxShadow: '0 6px 25px rgba(129, 199, 132, 0.6)',
                            transform: 'translateY(-2px)',
                          },
                          transition: 'all 0.3s ease',
                        }}
                      >
                        {executing ? '執行中...' : '執行查詢'}
                      </Button>
                    </Box>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 3,
                        mb: 3,
                        background: 'linear-gradient(135deg, #0d1117 0%, #1a1f2e 100%)',
                        color: '#4ade80',
                        fontFamily: '"Fira Code", "Roboto Mono", monospace',
                        fontSize: '0.95rem',
                        overflow: 'auto',
                        border: '1px solid rgba(74, 222, 128, 0.3)',
                        borderRadius: 2,
                        boxShadow: 'inset 0 2px 10px rgba(0, 0, 0, 0.5)',
                      }}
                    >
                      <pre style={{ margin: 0, whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                        {sql}
                      </pre>
                    </Paper>

                    {queryResults && (
                      <MotionBox
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                      >
                        <Typography variant="h6" gutterBottom>
                          查詢結果 ({queryResults.row_count} 筆)
                        </Typography>
                        <TableContainer
                          component={Paper}
                          elevation={0}
                          sx={{
                            maxHeight: 500,
                            background: 'rgba(26, 35, 50, 0.6)',
                            border: '1px solid rgba(100, 181, 246, 0.2)',
                            borderRadius: 2,
                            overflow: 'auto',
                          }}
                        >
                          <Table stickyHeader>
                            <TableHead>
                              <TableRow>
                                {queryResults.columns.map((column) => (
                                  <TableCell
                                    key={column}
                                    sx={{
                                      background: 'rgba(26, 35, 50, 0.95)',
                                      backdropFilter: 'blur(10px)',
                                      color: '#64b5f6',
                                      fontWeight: 'bold',
                                      borderBottom: '2px solid rgba(100, 181, 246, 0.3)',
                                      position: 'sticky',
                                      top: 0,
                                      zIndex: 10,
                                    }}
                                  >
                                    {column}
                                  </TableCell>
                                ))}
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {queryResults.rows.map((row, index) => (
                                <TableRow
                                  key={index}
                                  sx={{
                                    '&:hover': {
                                      background: 'rgba(100, 181, 246, 0.05)',
                                    },
                                  }}
                                >
                                  {queryResults.columns.map((column) => (
                                    <TableCell
                                      key={column}
                                      sx={{
                                        color: 'rgba(255, 255, 255, 0.8)',
                                        borderBottom: '1px solid rgba(100, 181, 246, 0.1)',
                                      }}
                                    >
                                      {row[column] !== null ? String(row[column]) : 'NULL'}
                                    </TableCell>
                                  ))}
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </MotionBox>
                    )}
                  </MotionBox>
                )}

                <Divider sx={{ my: 4 }} />

                <Typography variant="h6" gutterBottom>
                  範例查詢
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {examples.map((example, index) => (
                    <Chip
                      key={index}
                      label={example}
                      onClick={() => handleExampleClick(example)}
                      sx={{
                        cursor: 'pointer',
                        background: 'rgba(100, 181, 246, 0.1)',
                        border: '1px solid rgba(100, 181, 246, 0.3)',
                        color: '#64b5f6',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          background: 'rgba(100, 181, 246, 0.2)',
                          borderColor: '#64b5f6',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 4px 12px rgba(100, 181, 246, 0.3)',
                        },
                      }}
                    />
                  ))}
                </Box>
              </MotionPaper>
            )}

            {tabIndex === 1 && (
              <MotionPaper
                key="help"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ duration: 0.3 }}
                elevation={0}
                sx={{
                  p: 4,
                  background: 'rgba(26, 35, 50, 0.8)',
                  border: '1px solid rgba(100, 181, 246, 0.2)',
                  borderRadius: 2,
                }}
              >
                <Typography variant="h5" gutterBottom>
                  使用說明
                </Typography>

                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      1. 選擇模型提供者
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>本地模型：</strong> 使用本機運行的 Qwen 模型，無需 API 金鑰
                      <br />
                      <strong>AWS Bedrock：</strong> 使用 Claude Sonnet 4/4.5 模型
                      <br />
                      <strong>Google GenAI：</strong> 使用 Gemini 2.5 Pro/Flash 模型
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      2. 輸入自然語言查詢
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      用中文或英文描述你想要查詢的內容，系統會自動轉換為 SQL 語句。
                      <br />
                      範例：「查詢 2024 年 1 月的所有帳單」
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      3. 查看生成的 SQL
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      系統會生成對應的 SQL 查詢語句，你可以直接在資料庫中執行。
                    </Typography>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      4. 支援的資料表
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>tencent_bill：</strong> 騰訊帳單主表
                      <br />
                      <strong>global_bill：</strong> 全球帳單彙總表
                      <br />
                      <strong>global_bill_l3：</strong> 全球帳單明細表
                    </Typography>
                  </CardContent>
                </Card>
              </MotionPaper>
            )}

            {tabIndex === 2 && (
              <MotionPaper
                key="schema"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ duration: 0.3 }}
                elevation={0}
                sx={{
                  p: 4,
                  background: 'rgba(26, 35, 50, 0.8)',
                  border: '1px solid rgba(100, 181, 246, 0.2)',
                  borderRadius: 2,
                }}
              >
                <Typography variant="h5" gutterBottom>
                  資料庫結構
                </Typography>

                {schema && (
                  <List>
                    {schema.tables.map((table) => (
                      <Box key={table.name} sx={{ mb: 2 }}>
                        <Paper sx={{ p: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h6" sx={{ flex: 1 }}>
                              {table.name}
                            </Typography>
                            <IconButton onClick={() => toggleTable(table.name)}>
                              {expandedTable === table.name ? (
                                <ExpandLessIcon />
                              ) : (
                                <ExpandMoreIcon />
                              )}
                            </IconButton>
                          </Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {table.comment}
                          </Typography>

                          <Collapse in={expandedTable === table.name}>
                            <Divider sx={{ mb: 2 }} />
                            <List dense>
                              {table.columns.map((column) => (
                                <ListItem key={column.name}>
                                  <ListItemText
                                    primary={
                                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                        <Typography
                                          component="span"
                                          sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}
                                        >
                                          {column.name}
                                        </Typography>
                                        <Chip label={column.type} size="small" />
                                        {column.nullable === 'NO' && (
                                          <Chip label="NOT NULL" size="small" color="error" />
                                        )}
                                        {column.key === 'PRI' && (
                                          <Chip label="PRIMARY KEY" size="small" color="primary" />
                                        )}
                                      </Box>
                                    }
                                    secondary={column.comment}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </Collapse>
                        </Paper>
                      </Box>
                    ))}
                  </List>
                )}
              </MotionPaper>
            )}
          </AnimatePresence>
        </Container>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity={snackbar.severity}
            variant="filled"
            sx={{
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
              '& .MuiAlert-icon': {
                fontSize: '1.5rem',
              },
            }}
            action={
              <IconButton
                size="small"
                aria-label="close"
                color="inherit"
                onClick={handleCloseSnackbar}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            }
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;

