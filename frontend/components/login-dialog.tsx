"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiClient, type User as UserType } from "@/lib/api"

// Google OAuth types
declare global {
  interface Window {
    google: any;
  }
}

interface LoginDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onLogin: (user: UserType) => void
}

export function LoginDialog({ open, onOpenChange, onLogin }: LoginDialogProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [fullName, setFullName] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [activeTab, setActiveTab] = useState("login")
  const [googleLoaded, setGoogleLoaded] = useState(false)

  useEffect(() => {
    // Load Google OAuth script
    const loadGoogleScript = () => {
      console.log('Loading Google script...')
      if (window.google) {
        console.log('Google already loaded')
        setGoogleLoaded(true)
        return
      }

      const script = document.createElement('script')
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      script.onload = () => {
        console.log('Google script loaded successfully')
        setGoogleLoaded(true)
      }
      script.onerror = () => {
        console.error('Failed to load Google script')
      }
      document.head.appendChild(script)
    }

    loadGoogleScript()
  }, [])

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      setError("Please fill in all fields")
      return
    }

    setLoading(true)
    setError("")

    try {
      const userData = await apiClient.login(email, password)
      onLogin(userData)
      onOpenChange(false)
      
      // Reset form
      setEmail("")
      setPassword("")
      setActiveTab("login")
    } catch (error) {
      setError(error instanceof Error ? error.message : "Login failed")
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async () => {
    if (!email.trim() || !password.trim() || !fullName.trim() || !confirmPassword.trim()) {
      setError("Please fill in all fields")
      return
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }

    setLoading(true)
    setError("")

    try {
      await apiClient.register(email, password, fullName)
      
      // Auto login after registration
      const userData = await apiClient.login(email, password)
      onLogin(userData)
      onOpenChange(false)
      
      // Reset form
      setEmail("")
      setPassword("")
      setFullName("")
      setConfirmPassword("")
      setActiveTab("login")
    } catch (error) {
      setError(error instanceof Error ? error.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async (credential: string) => {
    setLoading(true)
    setError("")

    try {
      const userData = await apiClient.googleLogin(credential)
      onLogin(userData)
      onOpenChange(false)
      
      // Reset form
      setEmail("")
      setPassword("")
      setActiveTab("login")
    } catch (error) {
      if (error instanceof Error && (error.message.includes('not found') || error.message.includes('Chưa đăng ký'))) {
        setError("Chưa đăng ký, vui lòng liên hệ admin")
      } else {
        setError(error instanceof Error ? error.message : "Google login failed")
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    console.log('Google useEffect triggered:', { googleLoaded, hasGoogle: !!window.google, open, clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID })
    if (googleLoaded && window.google && open) {
      console.log('Initializing Google Sign-In...')
      window.google.accounts.id.initialize({
        client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
        callback: (response: any) => {
          console.log('Google login callback triggered')
          handleGoogleLogin(response.credential)
        }
      })

      // Wait for DOM to be ready, then render the button
      const renderGoogleButton = () => {
        const googleButtonElement = document.getElementById('google-signin-button')
        console.log('Google button element:', googleButtonElement)
        if (googleButtonElement) {
          console.log('Rendering Google button...')
          window.google.accounts.id.renderButton(
            googleButtonElement,
            {
              theme: 'outline',
              size: 'large',
              width: '100%',
              text: 'signin_with'
            }
          )
          console.log('Google button rendered')
        } else {
          console.error('Google button element not found, retrying...')
          // Retry after a short delay
          setTimeout(renderGoogleButton, 100)
        }
      }

      // Use setTimeout to ensure DOM is ready
      setTimeout(renderGoogleButton, 50)
    }
  }, [googleLoaded, open])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Welcome to AI Blog Pro</DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>
          
          <TabsContent value="login" className="space-y-4">
            <div>
              <Label htmlFor="login-email">Email</Label>
              <Input 
                id="login-email" 
                type="email"
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="Enter your email" 
                disabled={loading}
              />
            </div>
            <div>
              <Label htmlFor="login-password">Password</Label>
              <Input 
                id="login-password" 
                type="password"
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="Enter your password" 
                disabled={loading}
              />
            </div>
            {error && (
              <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                {error}
              </div>
            )}
            <Button onClick={handleLogin} className="w-full" disabled={loading}>
              {loading ? "Logging in..." : "Login"}
            </Button>
            
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
              </div>
            </div>
            
            {/* Google Sign-in Button */}
            <div id="google-signin-button" className="w-full"></div>
            
            {/* Fallback Google Button when Google SDK is not loaded or no Client ID */}
            {(!googleLoaded || !process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID === 'your_google_client_id_here') && (
              <Button 
                variant="outline" 
                className="w-full flex items-center justify-center gap-2" 
                onClick={() => setError("Google login is not configured. Please contact administrator.")}
                disabled={loading}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </Button>
            )}
          </TabsContent>
          
          <TabsContent value="register" className="space-y-4">
            <div>
              <Label htmlFor="register-name">Full Name</Label>
              <Input 
                id="register-name" 
                value={fullName} 
                onChange={(e) => setFullName(e.target.value)} 
                placeholder="Enter your full name" 
                disabled={loading}
              />
            </div>
            <div>
              <Label htmlFor="register-email">Email</Label>
              <Input 
                id="register-email" 
                type="email"
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="Enter your email" 
                disabled={loading}
              />
            </div>
            <div>
              <Label htmlFor="register-password">Password</Label>
              <Input 
                id="register-password" 
                type="password"
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="Enter your password" 
                disabled={loading}
              />
            </div>
            <div>
              <Label htmlFor="confirm-password">Confirm Password</Label>
              <Input 
                id="confirm-password" 
                type="password"
                value={confirmPassword} 
                onChange={(e) => setConfirmPassword(e.target.value)} 
                placeholder="Confirm your password" 
                disabled={loading}
              />
            </div>
            {error && (
              <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                {error}
              </div>
            )}
            <Button onClick={handleRegister} className="w-full" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </Button>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
