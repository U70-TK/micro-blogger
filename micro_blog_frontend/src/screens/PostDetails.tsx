import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Typography, Box, TextField, Button, Avatar } from '@mui/material'
import { BASE_URL } from '../api'

export default function PostDetails() {
  const { id } = useParams()
  const [post, setPost] = useState<any | null>(null)
  const [reply, setReply] = useState('')

  useEffect(() => {
    if (!id) return
    fetch(`${BASE_URL}/posts/${id}`)
      .then((r) => r.json())
      .then((d) => setPost(d))
      .catch(() => setPost(null))
  }, [id])

  const submitReply = async () => {
    if (!id) return
    await fetch(`${BASE_URL}/posts/${id}/reply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      body: JSON.stringify({ content: reply }),
    })
    setReply('')
    // refresh
    fetch(`${BASE_URL}/posts/${id}`).then((r) => r.json()).then((d) => setPost(d))
  }

  if (!post) return <Typography>Post not found</Typography>

  return (
    <Box sx={{ maxWidth: 720, mx: 'auto' }}>
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Avatar />
        <Box>
          <Typography variant="h6">{post.display_name || post.username}</Typography>
          <Typography variant="caption">@{post.username} · {new Date(post.created_at).toLocaleString()}</Typography>
        </Box>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Typography variant="body1">{post.content}</Typography>
      </Box>

      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle1">Replies</Typography>
        {post.replies && post.replies.length === 0 && <Typography>No replies yet</Typography>}
        {post.replies && post.replies.map((r: any) => (
          <Box key={r.id} sx={{ mt: 2, p: 2, border: '1px solid #eee', borderRadius: 1 }}>
            <Typography variant="body2"><strong>{r.username}</strong></Typography>
            <Typography>{r.content}</Typography>
            <Typography variant="caption">{new Date(r.created_at).toLocaleString()}</Typography>
          </Box>
        ))}
      </Box>

      <Box sx={{ mt: 3 }}>
        <TextField label="Reply" fullWidth multiline rows={3} value={reply} onChange={(e) => setReply(e.target.value)} sx={{ mb: 2 }} />
        <Button variant="contained" onClick={submitReply}>Reply</Button>
      </Box>
    </Box>
  )
}
