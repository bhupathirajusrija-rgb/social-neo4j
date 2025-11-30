import { useState, useEffect } from 'react'
import './App.css'
import { 
  health, register, login, getProfile, updateProfile,
  follow, unfollow, getConnections, getMutualConnections,
  recommendations, searchUsers, getPopularUsers, feed 
} from './api'

function App() {
  const [activeTab, setActiveTab] = useState('register')
  const [status, setStatus] = useState('Ready')
  const [statusType, setStatusType] = useState('info')
  const [loading, setLoading] = useState(false)
  
  // Authentication
  const [currentUser, setCurrentUser] = useState(null)
  const [loginUsername, setLoginUsername] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  
  // Registration
  const [regUsername, setRegUsername] = useState('')
  const [regName, setRegName] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')
  
  // Profile
  const [profile, setProfile] = useState(null)
  const [editName, setEditName] = useState('')
  const [editEmail, setEditEmail] = useState('')
  const [editBio, setEditBio] = useState('')
  
  // Follow
  const [followUsername, setFollowUsername] = useState('')
  const [connections, setConnections] = useState(null)
  
  // Mutual connections
  const [mutualUser, setMutualUser] = useState('')
  const [mutualConnections, setMutualConnections] = useState([])
  
  // Recommendations
  const [userRecs, setUserRecs] = useState([])
  
  // Search
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  
  // Popular users
  const [popularUsers, setPopularUsers] = useState([])
  
  // Feed
  const [userFeed, setUserFeed] = useState([])

  useEffect(() => {
    checkHealth()
    // Load popular users on mount
    loadPopularUsers()
  }, [])

  const showStatus = (message, type = 'info') => {
    setStatus(message)
    setStatusType(type)
  }

  const checkHealth = async () => {
    try {
      const result = await health()
      if (result.status === 'ok' && result.db) {
        showStatus('✓ System healthy - Database connected', 'success')
      } else {
        showStatus('⚠ System healthy but database disconnected', 'error')
      }
    } catch (error) {
      showStatus(`✗ Error: ${error.message}`, 'error')
    }
  }

  // UC-1: User Registration
  const handleRegister = async () => {
    if (!regUsername.trim() || !regName.trim() || !regEmail.trim() || !regPassword.trim()) {
      showStatus('Please fill in all fields', 'error')
      return
    }
    
    setLoading(true)
    try {
      const user = await register(regUsername.trim(), regName.trim(), regEmail.trim(), regPassword)
      setCurrentUser(user)
      showStatus(`✓ Successfully registered as ${user.username}`, 'success')
      setRegUsername('')
      setRegName('')
      setRegEmail('')
      setRegPassword('')
      setActiveTab('profile')
      loadProfile(user.username)
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-2: User Login
  const handleLogin = async () => {
    if (!loginUsername.trim() || !loginPassword.trim()) {
      showStatus('Please enter username and password', 'error')
      return
    }
    
    setLoading(true)
    try {
      const user = await login(loginUsername.trim(), loginPassword)
      setCurrentUser(user)
      showStatus(`✓ Successfully logged in as ${user.username}`, 'success')
      setLoginUsername('')
      setLoginPassword('')
      setActiveTab('profile')
      loadProfile(user.username)
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-3: View Profile
  const loadProfile = async (username) => {
    if (!username) username = currentUser?.username
    if (!username) {
      showStatus('Please login first', 'error')
      return
    }
    
    setLoading(true)
    try {
      const profileData = await getProfile(username)
      setProfile(profileData)
      setEditName(profileData.name || '')
      setEditEmail(profileData.email || '')
      setEditBio(profileData.bio || '')
      showStatus(`✓ Profile loaded`, 'success')
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-4: Edit Profile
  const handleUpdateProfile = async () => {
    if (!currentUser) {
      showStatus('Please login first', 'error')
      return
    }
    
    setLoading(true)
    try {
      const updateData = {}
      if (editName !== profile.name) updateData.name = editName
      if (editEmail !== profile.email) updateData.email = editEmail
      if (editBio !== profile.bio) updateData.bio = editBio
      
      if (Object.keys(updateData).length === 0) {
        showStatus('No changes to save', 'info')
        return
      }
      
      const updated = await updateProfile(currentUser.username, updateData)
      setProfile(updated)
      setCurrentUser(updated)
      showStatus(`✓ Profile updated successfully`, 'success')
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-5: Follow User
  const handleFollow = async (targetUser = null) => {
    const userToFollow = targetUser || followUsername.trim()
    if (!currentUser) {
      showStatus('Please login first', 'error')
      return
    }
    if (!userToFollow) {
      showStatus('Please enter a username to follow', 'error')
      return
    }
    
    setLoading(true)
    try {
      await follow(currentUser.username, userToFollow)
      showStatus(`✓ Now following ${userToFollow}`, 'success')
      setFollowUsername('')
      if (connections) loadConnections()
      if (userRecs.length > 0) loadRecommendations()
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-6: Unfollow User
  const handleUnfollow = async (targetUser) => {
    if (!currentUser) {
      showStatus('Please login first', 'error')
      return
    }
    
    setLoading(true)
    try {
      await unfollow(currentUser.username, targetUser)
      showStatus(`✓ Unfollowed ${targetUser}`, 'success')
      if (connections) loadConnections()
      if (userRecs.length > 0) loadRecommendations()
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-7: View Connections
  const loadConnections = async () => {
    if (!currentUser) {
      showStatus('Please login first', 'error')
      return
    }
    
    setLoading(true)
    try {
      const conns = await getConnections(currentUser.username)
      setConnections(conns)
      showStatus(`✓ Loaded connections`, 'success')
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-8: Mutual Connections
  const loadMutualConnections = async () => {
    if (!currentUser || !mutualUser.trim()) {
      showStatus('Please login and enter a username', 'error')
      return
    }
    
    setLoading(true)
    try {
      const mutual = await getMutualConnections(currentUser.username, mutualUser.trim())
      setMutualConnections(mutual)
      if (mutual.length > 0) {
        showStatus(`✓ Found ${mutual.length} mutual connections`, 'success')
      } else {
        showStatus('No mutual connections found', 'info')
      }
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-9: Recommendations
  const loadRecommendations = async () => {
    if (!currentUser) {
      showStatus('Please login first', 'error')
      return
    }
    
    setLoading(true)
    try {
      const recs = await recommendations(currentUser.username)
      setUserRecs(recs)
      if (recs.length > 0) {
        showStatus(`✓ Found ${recs.length} recommendations`, 'success')
      } else {
        showStatus('No recommendations available. Follow some users first!', 'info')
      }
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-10: Search Users
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      showStatus('Please enter a search query', 'error')
      return
    }
    
    setLoading(true)
    try {
      const results = await searchUsers(searchQuery.trim())
      setSearchResults(results)
      if (results.length > 0) {
        showStatus(`✓ Found ${results.length} users`, 'success')
      } else {
        showStatus('No users found', 'info')
      }
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  // UC-11: Popular Users
  const loadPopularUsers = async () => {
    try {
      const popular = await getPopularUsers(20)
      setPopularUsers(popular)
    } catch (error) {
      console.error('Error loading popular users:', error)
    }
  }

  // Feed
  const loadFeed = async () => {
    if (!currentUser) {
      showStatus('Please login first', 'error')
      return
    }
    
    setLoading(true)
    try {
      const feedData = await feed(currentUser.username)
      setUserFeed(feedData)
      if (feedData.length > 0) {
        showStatus(`✓ Found ${feedData.length} posts in feed`, 'success')
      } else {
        showStatus('No posts in feed. Follow users who have posted!', 'info')
      }
    } catch (error) {
      showStatus(`✗ Error: ${error.response?.data?.detail || error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    setCurrentUser(null)
    setProfile(null)
    setConnections(null)
    setUserRecs([])
    setSearchResults([])
    setUserFeed([])
    setActiveTab('register')
    showStatus('Logged out', 'info')
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>NeoSphere</h1>
        <p className="subtitle">A smarter way to stay connected!</p>
        {currentUser && (
          <div className="user-header">
            <span>Logged in as: <strong>{currentUser.username}</strong></span>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </div>
        )}
      </header>

      <div className={`status-bar status-${statusType}`}>
        <span>{status}</span>
        <button className="icon-button" onClick={checkHealth} title="Refresh health">🔄</button>
      </div>

      <div className="tabs">
        <button className={activeTab === 'register' ? 'tab active' : 'tab'} onClick={() => setActiveTab('register')}>
          Register
        </button>
        <button className={activeTab === 'login' ? 'tab active' : 'tab'} onClick={() => setActiveTab('login')}>
          Login
        </button>
        <button className={activeTab === 'profile' ? 'tab active' : 'tab'} onClick={() => { setActiveTab('profile'); if (currentUser) loadProfile(); }}>
          Profile
        </button>
        <button className={activeTab === 'follow' ? 'tab active' : 'tab'} onClick={() => { setActiveTab('follow'); if (currentUser) loadConnections(); }}>
          Follow
        </button>
        <button className={activeTab === 'mutual' ? 'tab active' : 'tab'} onClick={() => setActiveTab('mutual')}>
          Mutual
        </button>
        <button className={activeTab === 'recommendations' ? 'tab active' : 'tab'} onClick={() => { setActiveTab('recommendations'); if (currentUser) loadRecommendations(); }}>
          Recommendations
        </button>
        <button className={activeTab === 'search' ? 'tab active' : 'tab'} onClick={() => setActiveTab('search')}>
          Search
        </button>
        <button className={activeTab === 'popular' ? 'tab active' : 'tab'} onClick={() => { setActiveTab('popular'); loadPopularUsers(); }}>
          Popular
        </button>
        <button className={activeTab === 'feed' ? 'tab active' : 'tab'} onClick={() => { setActiveTab('feed'); if (currentUser) loadFeed(); }}>
          Feed
        </button>
      </div>

      <div className="main-content">
        {/* UC-1: Registration */}
        {activeTab === 'register' && (
          <div className="card">
            <h2>UC-1: User Registration</h2>
            <div className="form-group">
              <input type="text" placeholder="Username" value={regUsername} onChange={(e) => setRegUsername(e.target.value)} disabled={loading} />
              <input type="text" placeholder="Full Name" value={regName} onChange={(e) => setRegName(e.target.value)} disabled={loading} />
              <input type="email" placeholder="Email" value={regEmail} onChange={(e) => setRegEmail(e.target.value)} disabled={loading} />
              <input type="password" placeholder="Password" value={regPassword} onChange={(e) => setRegPassword(e.target.value)} disabled={loading} />
              <button onClick={handleRegister} disabled={loading} className="btn-primary">
                {loading ? 'Registering...' : 'Register'}
              </button>
            </div>
          </div>
        )}

        {/* UC-2: Login */}
        {activeTab === 'login' && (
          <div className="card">
            <h2>UC-2: User Login</h2>
            <div className="form-group">
              <input type="text" placeholder="Username" value={loginUsername} onChange={(e) => setLoginUsername(e.target.value)} disabled={loading} />
              <input type="password" placeholder="Password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} disabled={loading} onKeyPress={(e) => e.key === 'Enter' && handleLogin()} />
              <button onClick={handleLogin} disabled={loading} className="btn-primary">
                {loading ? 'Logging in...' : 'Login'}
              </button>
            </div>
          </div>
        )}

        {/* UC-3/4: Profile */}
        {activeTab === 'profile' && (
          <div className="card">
            <h2>UC-3: View Profile | UC-4: Edit Profile</h2>
            {!currentUser ? (
              <p className="hint">Please login first</p>
            ) : (
              <>
                <button onClick={() => loadProfile()} className="btn-secondary" style={{marginBottom: '1rem'}}>Refresh Profile</button>
                {profile ? (
                  <div>
                    <div className="profile-view">
                      <p><strong>Username:</strong> {profile.username}</p>
                      <p><strong>Name:</strong> {profile.name}</p>
                      <p><strong>Email:</strong> {profile.email}</p>
                      <p><strong>Bio:</strong> {profile.bio || 'No bio'}</p>
                      <p><strong>Following:</strong> {profile.followingCount || 0}</p>
                      <p><strong>Followers:</strong> {profile.followersCount || 0}</p>
                    </div>
                    <div className="form-group" style={{marginTop: '1.5rem'}}>
                      <h3>Edit Profile</h3>
                      <input type="text" placeholder="Name" value={editName} onChange={(e) => setEditName(e.target.value)} disabled={loading} />
                      <input type="email" placeholder="Email" value={editEmail} onChange={(e) => setEditEmail(e.target.value)} disabled={loading} />
                      <textarea placeholder="Bio" value={editBio} onChange={(e) => setEditBio(e.target.value)} disabled={loading} rows="3" />
                      <button onClick={handleUpdateProfile} disabled={loading} className="btn-primary">
                        {loading ? 'Updating...' : 'Update Profile'}
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="hint">Click "Refresh Profile" to load</p>
                )}
              </>
            )}
          </div>
        )}

        {/* UC-5/6/7: Follow */}
        {activeTab === 'follow' && (
          <div className="card">
            <h2>UC-5: Follow | UC-6: Unfollow | UC-7: View Connections</h2>
            {!currentUser ? (
              <p className="hint">Please login first</p>
            ) : (
              <>
                <div className="form-group">
                  <input type="text" placeholder="Username to follow" value={followUsername} onChange={(e) => setFollowUsername(e.target.value)} disabled={loading} onKeyPress={(e) => e.key === 'Enter' && handleFollow()} />
                  <button onClick={() => handleFollow()} disabled={loading || !followUsername.trim()} className="btn-primary">
                    {loading ? 'Following...' : 'Follow'}
                  </button>
                </div>
                <button onClick={loadConnections} className="btn-secondary" style={{marginBottom: '1rem'}}>Load Connections</button>
                {connections && (
                  <div className="connections">
                    <div>
                      <h3>Following ({connections.following.length})</h3>
                      <div className="user-list">
                        {connections.following.map((user, idx) => (
                          <div key={idx} className="user-item">
                            <strong>{user.username}</strong> - {user.name}
                            <button onClick={() => handleUnfollow(user.username)} className="btn-small" disabled={loading}>Unfollow</button>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3>Followers ({connections.followers.length})</h3>
                      <div className="user-list">
                        {connections.followers.map((user, idx) => (
                          <div key={idx} className="user-item">
                            <strong>{user.username}</strong> - {user.name}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* UC-8: Mutual Connections */}
        {activeTab === 'mutual' && (
          <div className="card">
            <h2>UC-8: Mutual Connections</h2>
            {!currentUser ? (
              <p className="hint">Please login first</p>
            ) : (
              <>
                <div className="form-group">
                  <input type="text" placeholder="Other username" value={mutualUser} onChange={(e) => setMutualUser(e.target.value)} disabled={loading} onKeyPress={(e) => e.key === 'Enter' && loadMutualConnections()} />
                  <button onClick={loadMutualConnections} disabled={loading || !mutualUser.trim()} className="btn-primary">
                    {loading ? 'Loading...' : 'Find Mutual Connections'}
                  </button>
                </div>
                {mutualConnections.length > 0 && (
                  <div className="user-list">
                    {mutualConnections.map((user, idx) => (
                      <div key={idx} className="user-item">
                        <strong>{user.username}</strong> - {user.name}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* UC-9: Recommendations */}
        {activeTab === 'recommendations' && (
          <div className="card">
            <h2>UC-9: Friend Recommendations</h2>
            {!currentUser ? (
              <p className="hint">Please login first</p>
            ) : (
              <>
                <button onClick={loadRecommendations} disabled={loading} className="btn-primary" style={{marginBottom: '1rem'}}>
                  {loading ? 'Loading...' : 'Get Recommendations'}
                </button>
                {userRecs.length > 0 && (
                  <div className="recommendations-list">
                    {userRecs.map((rec, idx) => (
                      <div key={idx} className="recommendation-item">
                        <div className="rec-info">
                          <strong>{rec.username}</strong>
                          <span>{rec.name}</span>
                          {rec.bio && <span className="bio">{rec.bio}</span>}
                          <span className="score">Score: {rec.score}</span>
                        </div>
                        <button onClick={() => handleFollow(rec.username)} className="btn-small" disabled={loading}>Follow</button>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* UC-10: Search */}
        {activeTab === 'search' && (
          <div className="card">
            <h2>UC-10: Search Users</h2>
            <div className="form-group">
              <input type="text" placeholder="Search by username or name" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} disabled={loading} onKeyPress={(e) => e.key === 'Enter' && handleSearch()} />
              <button onClick={handleSearch} disabled={loading || !searchQuery.trim()} className="btn-primary">
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
            {searchResults.length > 0 && (
              <div className="user-list">
                {searchResults.map((user, idx) => (
                  <div key={idx} className="user-item">
                    <strong>{user.username}</strong> - {user.name}
                    {user.bio && <span className="bio">{user.bio}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* UC-11: Popular Users */}
        {activeTab === 'popular' && (
          <div className="card">
            <h2>UC-11: Explore Popular Users</h2>
            <button onClick={loadPopularUsers} className="btn-secondary" style={{marginBottom: '1rem'}}>Refresh</button>
            {popularUsers.length > 0 && (
              <div className="user-list">
                {popularUsers.map((item, idx) => (
                  <div key={idx} className="user-item">
                    <strong>{item.user.username}</strong> - {item.user.name}
                    <span className="score">👥 {item.followersCount} followers</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Feed */}
        {activeTab === 'feed' && (
          <div className="card">
            <h2>Feed</h2>
            {!currentUser ? (
              <p className="hint">Please login first</p>
            ) : (
              <>
                <button onClick={loadFeed} disabled={loading} className="btn-primary" style={{marginBottom: '1rem'}}>
                  {loading ? 'Loading...' : 'Refresh Feed'}
                </button>
                {userFeed.length > 0 && (
                  <div className="feed-list">
                    {userFeed.map((post, idx) => (
                      <div key={idx} className="feed-item">
                        <div className="feed-author">
                          <strong>@{post.author}</strong>
                          {post.createdAt && <span className="feed-date">{new Date(post.createdAt).toLocaleString()}</span>}
                        </div>
                        <div className="feed-content">{post.text || 'No content'}</div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
