import React, { useState } from 'react'
import { TextField, Button, Box, Typography, Alert } from '@mui/material'
import { BASE_URL } from '../api'
import { useNavigate } from 'react-router-dom'

export default function NewPost() {
  const [content, setContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const res = await fetch(`${BASE_URL}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
        body: JSON.stringify({ content }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || 'Could not create post')
        return
      }
      const data = await res.json()
      navigate(`/posts/${data.id}`)
    } catch (err) {
      setError('Network error')
    }
  }

  return (
    <Box sx={{ maxWidth: 720, mx: 'auto' }}>
      <Typography variant="h5" sx={{ mb: 2 }}>Create new post</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <form onSubmit={submit}>
        <TextField label="What's happening?" multiline rows={4} fullWidth sx={{ mb: 2 }} value={content} onChange={(e) => setContent(e.target.value)} />
        <Button variant="contained" type="submit">Post</Button>
      </form>
    </Box>
  )
}
