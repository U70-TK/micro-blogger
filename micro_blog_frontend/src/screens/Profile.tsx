import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Typography, Box, Avatar, Button, TextField, Alert } from '@mui/material'
import { BASE_URL } from '../api'

export default function Profile() {
  const params = useParams()
  const navigate = useNavigate()
  const [profile, setProfile] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [displayName, setDisplayName] = useState('')
  const [bio, setBio] = useState('')
  const [avatarUrl, setAvatarUrl] = useState('')
  const [error, setError] = useState<string | null>(null)

  const username = params.username

  useEffect(() => {
    const token = localStorage.getItem('token') || ''
    if (username) {
      fetch(`${BASE_URL}/users/${username}`)
        .then((r) => r.json())
        .then((d) => setProfile(d))
        .catch(() => setProfile(null))
        .finally(() => setLoading(false))
      return
    }

    // No username provided: get current user's username via /me, then fetch profile
    fetch(`${BASE_URL}/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => {
        if (!r.ok) throw new Error('not authorized')
        return r.json()
      })
      .then((me) => fetch(`${BASE_URL}/users/${me.username}`))
      .then((r) => r.json())
      .then((d) => setProfile(d))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false))
  }, [username])

  useEffect(() => {
    if (profile) {
      setDisplayName(profile.display_name || '')
      setBio(profile.bio || '')
      setAvatarUrl(profile.avatar_url || '')
    }
  }, [profile])

  if (loading) return <Typography>Loading...</Typography>
  if (!profile) return <Typography>Profile not found</Typography>

  const save = async () => {
    setError(null)
    try {
      const res = await fetch(`${BASE_URL}/me`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
        body: JSON.stringify({ display_name: displayName, bio, avatar_url: avatarUrl }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || 'Could not save')
        return
      }
      setEditMode(false)
      navigate('/me')
    } catch (err) {
      setError('Network error')
    }
  }

  return (
    <Box sx={{ maxWidth: 920, mx: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, justifyContent: 'space-between' }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h5">{profile.display_name || profile.username}</Typography>
          <Typography variant="body2" color="text.secondary">@{profile.username}</Typography>
        </Box>
        <Avatar src={profile.avatar_url || undefined} sx={{ width: 96, height: 96, ml: 2 }} />
      </Box>

      <Box sx={{ mt: 3 }}>
        {username ? null : (
          <Button variant="outlined" onClick={() => setEditMode(!editMode)} sx={{ mb: 2 }}>
            {editMode ? 'Cancel' : 'Edit Profile'}
          </Button>
        )}

        {error && <Alert severity="error">{error}</Alert>}

        {editMode ? (
          <Box>
            <TextField label="Display name" fullWidth sx={{ mb: 2 }} value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
            <TextField label="Bio" fullWidth multiline rows={3} sx={{ mb: 2 }} value={bio} onChange={(e) => setBio(e.target.value)} />
            <TextField label="Avatar URL" fullWidth sx={{ mb: 2 }} value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} />
            <Button variant="contained" onClick={save}>Save</Button>
          </Box>
        ) : (
          <Typography sx={{ whiteSpace: 'pre-wrap' }}>{profile.bio}</Typography>
        )}

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6">Posts</Typography>
          {profile.posts && profile.posts.length === 0 && <Typography>No posts yet</Typography>}
          {profile.posts && profile.posts.map((p: any) => (
            <Box key={p.id} sx={{ mt: 2, p: 2, border: '1px solid #eee', borderRadius: 1 }}>
              <Typography>{p.content}</Typography>
              <Typography variant="caption" color="text.secondary">{new Date(p.created_at).toLocaleString()}</Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  )
}
