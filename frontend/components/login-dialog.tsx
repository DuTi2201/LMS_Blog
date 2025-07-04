"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiClient, type User as UserType } from "@/lib/api"

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
