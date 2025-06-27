"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Github, User, LogOut } from "lucide-react"
import { useState, useEffect } from "react"
import { LoginDialog } from "@/components/login-dialog"
import { apiClient } from "@/lib/api"

interface User {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
}

export function Header() {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (token) {
          const userData = await apiClient.getCurrentUser()
          setUser(userData)
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        localStorage.removeItem('access_token')
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const handleLogin = (userData: User) => {
    setUser(userData)
    setIsLoginOpen(false)
  }

  const handleLogout = async () => {
    try {
      await apiClient.logout()
      setUser(null)
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <>
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-500 rounded flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AI</span>
                </div>
                <span className="font-semibold text-gray-900">AI Blog Pro</span>
              </Link>

              <nav className="hidden md:flex space-x-6">
                <Link href="/" className="text-gray-700 hover:text-gray-900">
                  Home
                </Link>
                <Link href="/archive" className="text-gray-700 hover:text-gray-900">
                  Archive
                </Link>
                <Link href="/categories" className="text-gray-700 hover:text-gray-900">
                  Categories
                </Link>
                <Link href="/tags" className="text-gray-700 hover:text-gray-900">
                  Tags
                </Link>
                <Link href="/about" className="text-gray-700 hover:text-gray-900">
                  About
                </Link>
                <Link
                  href="https://github.com"
                  className="text-gray-700 hover:text-gray-900 flex items-center space-x-1"
                >
                  <span>GitHub</span>
                  <Github className="w-4 h-4" />
                </Link>
              </nav>
            </div>

            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input placeholder="Search" className="pl-10 w-64" />
              </div>

              {loading ? (
                <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
              ) : user ? (
                <div className="flex items-center space-x-2">
                  <Link href="/learning-path">
                    <Button variant="outline">Learning Path</Button>
                  </Link>
                  {(user.role === "admin" || user.role === "user") && (
                    <Link href="/blog-management">
                      <Button variant="outline">Manage Blog</Button>
                    </Link>
                  )}
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-medium">
                        {user.full_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <span className="text-sm text-gray-700 hidden md:block">{user.full_name}</span>
                    <Button variant="ghost" size="sm" onClick={handleLogout}>
                      <LogOut className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <Button onClick={() => setIsLoginOpen(true)}>
                  <User className="w-4 h-4 mr-2" />
                  Login
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      <LoginDialog open={isLoginOpen} onOpenChange={setIsLoginOpen} onLogin={handleLogin} />
    </>
  )
}
