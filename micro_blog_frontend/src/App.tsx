import React from 'react'
import './App.css'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material'
import Home from './screens/Home'
import Login from './screens/Login'
import Register from './screens/Register'
import Profile from './screens/Profile'
import NewPost from './screens/NewPost'
import PostDetails from './screens/PostDetails'

function App() {
  const token = localStorage.getItem('token')

  const logout = () => {
    localStorage.removeItem('token')
    window.location.href = '/'
  }

  return (
    <BrowserRouter>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            MicroBlogger
          </Typography>
          <Button color="inherit" component={Link} to="/">
            Home
          </Button>
          <Button color="inherit" component={Link} to="/new">
            New Post
          </Button>
          {!token ? (
            <>
              <Button color="inherit" component={Link} to="/login">
                Login
              </Button>
              <Button color="inherit" component={Link} to="/register">
                Register
              </Button>
            </>
          ) : (
            <>
              <Button color="inherit" component={Link} to="/me">
                Profile
              </Button>
              <Button color="inherit" onClick={logout}>
                Logout
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>

      <div className="app-container">
        <div className="app-header-spacer" />
        <Container sx={{ mt: 2 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/me" element={<Profile />} />
          <Route path="/users/:username" element={<Profile />} />
          <Route path="/new" element={<NewPost />} />
          <Route path="/posts/:id" element={<PostDetails />} />
        </Routes>
        </Container>
      </div>
    </BrowserRouter>
  )
}

export default App
