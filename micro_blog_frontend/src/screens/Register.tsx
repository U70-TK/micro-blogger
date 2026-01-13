import React, { useState } from 'react'
import { TextField, Button, Box, Typography, Alert } from '@mui/material'
import { BASE_URL } from '../api'
import { useNavigate } from 'react-router-dom'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  React.useEffect(() => {
    if (localStorage.getItem('token')) navigate('/me')
  }, [navigate])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const res = await fetch(`${BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || 'Registration failed')
        return
      }
      navigate('/login')
    } catch (err) {
      setError('Network error')
    }
  }

  return (
    <Box sx={{ maxWidth: 480, mx: 'auto' }}>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Create account
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <form onSubmit={submit}>
        <TextField label="Username" fullWidth sx={{ mb: 2 }} value={username} onChange={(e) => setUsername(e.target.value)} />
        <TextField label="Email" fullWidth sx={{ mb: 2 }} value={email} onChange={(e) => setEmail(e.target.value)} />
        <TextField label="Password" type="password" fullWidth sx={{ mb: 2 }} value={password} onChange={(e) => setPassword(e.target.value)} />
        <Button variant="contained" type="submit">Register</Button>
      </form>
    </Box>
  )
}
