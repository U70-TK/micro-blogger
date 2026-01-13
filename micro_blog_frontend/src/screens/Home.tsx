import React, { useEffect, useState } from 'react'
import { Card, CardContent, Typography, Grid, IconButton, CircularProgress } from '@mui/material'
import FavoriteIcon from '@mui/icons-material/Favorite'
import { Link } from 'react-router-dom'
import { BASE_URL } from '../api'

type Post = {
  id: number
  user_id: number
  content: string
  created_at: string
  username: string
  display_name?: string | null
  likes_count: number
  replies_count: number
}

export default function Home() {
  const [posts, setPosts] = useState<Post[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [liking, setLiking] = useState<number | null>(null)

  useEffect(() => {
    fetch(`${BASE_URL}/posts`)
      .then((r) => r.json())
      .then((data) => {
        setPosts(data)
        // refresh likes counts for each post via the new endpoint
        if (data && Array.isArray(data)) {
          Promise.all(
            data.map((p: Post) =>
              fetch(`${BASE_URL}/get_like_numbers_by_post_id?post_id=${p.id}`).then((r) => r.json()).catch(() => ({ post_id: p.id, likes_count: p.likes_count }))
            )
          ).then((counts: any[]) => {
            setPosts((prev) =>
              prev && prev.map((p) => {
                const c = counts.find((x) => x.post_id === p.id)
                return c ? { ...p, likes_count: c.likes_count } : p
              })
            )
          })
        }
      })
      .catch(() => setPosts([]))
      .finally(() => setLoading(false))
  }, [])

  const handleLike = async (postId: number) => {
    const token = localStorage.getItem('token') || ''
    setLiking(postId)
    try {
      const res = await fetch(`${BASE_URL}/posts/${postId}/like`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        // ignore or show error later
        setLiking(null)
        return
      }
      const data = await res.json().catch(() => ({}))
      // update local post likes_count if present
      setPosts((prev) => prev && prev.map((p) => (p.id === postId ? { ...p, likes_count: data.likes_count ?? p.likes_count } : p)))
    } catch (err) {
      // network error
    } finally {
      setLiking(null)
    }
  }

  if (loading) return <CircularProgress />

  return (
    <Grid container spacing={2}>
      {posts && posts.length === 0 && (
        <Typography>No posts yet — be the first to post!</Typography>
      )}
      {posts &&
        posts.map((p) => (
          <Grid item xs={12} md={6} key={p.id}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">
                  <Link to={`/users/${p.username}`}>{p.display_name || p.username}</Link> ·{' '}
                  <Typography component="span" variant="caption">{new Date(p.created_at).toLocaleString()}</Typography>
                </Typography>
                <Typography variant="body1" sx={{ mt: 1, mb: 2 }}>
                  {p.content}
                </Typography>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <IconButton aria-label="like" onClick={() => handleLike(p.id)} disabled={liking === p.id}>
                      <FavoriteIcon color={p.likes_count > 0 ? 'error' : 'inherit'} />
                    </IconButton>
                    <Typography component="span">{p.likes_count}</Typography>
                  </div>
                  <div>
                    <Link to={`/posts/${p.id}`}>View</Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Grid>
        ))}
    </Grid>
  )
}
