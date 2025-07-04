"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Edit, Trash2, Plus, Loader2, Users, BookOpen, UserCheck } from "lucide-react"
import { apiClient } from "@/lib/api"
import type { User, Course } from "@/lib/api"

interface UserWithCourses extends User {
  enrolledCourses?: Course[]
}

interface UserFormData {
  email: string
  full_name: string
  role: string
  courseIds: string[]
}

export default function UserManagementPage() {
  const [users, setUsers] = useState<UserWithCourses[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<UserWithCourses | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [roleFilter, setRoleFilter] = useState<string>("all")
  
  const [formData, setFormData] = useState<UserFormData>({
    email: "",
    full_name: "",
    role: "user",
    courseIds: []
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch users and courses
      const [usersData, coursesData] = await Promise.all([
        apiClient.getUsers(),
        apiClient.getCourses()
      ])
      
      // Fetch enrollments for each user
      const usersWithCourses = await Promise.all(
        usersData.map(async (user: User) => {
          try {
            const enrollments = await apiClient.getUserEnrollments(user.id)
            const enrolledCourses = enrollments.map((enrollment: any) => enrollment.course)
            return { ...user, enrolledCourses }
          } catch (error) {
            console.error(`Error fetching enrollments for user ${user.id}:`, error)
            return { ...user, enrolledCourses: [] }
          }
        })
      )
      
      setUsers(usersWithCourses)
      setCourses(coursesData)
    } catch (err) {
      console.error('Error fetching data:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data'
      setError(errorMessage)
      
      // If it's an authentication error, show a more specific message
      if (errorMessage.includes('Authentication required') || errorMessage.includes('Session expired')) {
        setError('Please login to access user management')
      }
    } finally {
      setLoading(false)
    }
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.full_name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = roleFilter === "all" || user.role === roleFilter
    return matchesSearch && matchesRole
  })

  const handleCreateUser = () => {
    setEditingUser(null)
    setFormData({
      email: "",
      full_name: "",
      role: "user",
      courseIds: []
    })
    setIsDialogOpen(true)
  }

  const handleEditUser = (user: UserWithCourses) => {
    setEditingUser(user)
    setFormData({
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      courseIds: user.enrolledCourses?.map(course => course.id) || []
    })
    setIsDialogOpen(true)
  }

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) {
      return
    }
    
    try {
      await apiClient.deleteUser(userId)
      setUsers(users.filter(user => user.id !== userId))
    } catch (error) {
      console.error('Error deleting user:', error)
      alert('Failed to delete user. Please try again.')
    }
  }

  const handleSaveUser = async () => {
    try {
      let savedUser
      
      if (editingUser) {
        // Update existing user
        const updateData = {
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role
        }
        
        savedUser = await apiClient.updateUser(editingUser.id, updateData)
        
        // Update course enrollments
        await updateUserEnrollments(editingUser.id, formData.courseIds)
      } else {
        // Create new user with course assignments
        savedUser = await apiClient.createUser({
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
          course_ids: formData.courseIds
        })
      }
      
      setIsDialogOpen(false)
      await fetchData() // Refresh data
    } catch (error) {
      console.error('Error saving user:', error)
      alert('Failed to save user. Please try again.')
    }
  }

  const updateUserEnrollments = async (userId: string, courseIds: string[]) => {
    try {
      // Get current enrollments
      const currentEnrollments = await apiClient.getUserEnrollments(userId)
      const currentCourseIds = currentEnrollments.map((e: any) => e.course.id)
      
      // Find courses to enroll and unenroll
      const toEnroll = courseIds.filter(id => !currentCourseIds.includes(id))
      const toUnenroll = currentCourseIds.filter((id: string) => !courseIds.includes(id))
      
      // Enroll in new courses
      for (const courseId of toEnroll) {
        await apiClient.enrollUserInCourse(userId, courseId)
      }
      
      // Unenroll from removed courses
      for (const courseId of toUnenroll) {
        await apiClient.unenrollUserFromCourse(userId, courseId)
      }
    } catch (error) {
      console.error('Error updating enrollments:', error)
      throw error
    }
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800'
      case 'instructor': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchData}>Try Again</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <Users className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          </div>
          <Button onClick={handleCreateUser} className="flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add New User</span>
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">All Users</p>
                  <p className="text-2xl font-bold">{users.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <UserCheck className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">Active Users</p>
                  <p className="text-2xl font-bold">{users.filter(u => u.is_active).length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">Instructors</p>
                  <p className="text-2xl font-bold">{users.filter(u => u.role === 'instructor').length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-red-600" />
                <div>
                  <p className="text-sm text-gray-600">Admins</p>
                  <p className="text-2xl font-bold">{users.filter(u => u.role === 'admin').length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <Label htmlFor="search">Search Users</Label>
                <Input
                  id="search"
                  placeholder="Search by username, email, or name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="w-full md:w-48">
                <Label htmlFor="role-filter">Filter by Role</Label>
                <Select value={roleFilter} onValueChange={setRoleFilter}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Roles</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="instructor">Instructor</SelectItem>
                    <SelectItem value="user">User</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Users ({filteredUsers.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Username</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Courses</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge className={getRoleBadgeColor(user.role)}>
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {user.enrolledCourses?.slice(0, 2).map((course) => (
                          <Badge key={course.id} variant="outline" className="text-xs">
                            {course.title}
                          </Badge>
                        ))}
                        {user.enrolledCourses && user.enrolledCourses.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{user.enrolledCourses.length - 2} more
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell>
                      {user.last_login_at ? formatDate(user.last_login_at) : 'Never'}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditUser(user)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* User Form Dialog */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingUser ? 'Edit User' : 'Create New User'}
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-6">
              <div>
                <Label htmlFor="email">Email (Google Account)</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="Enter Google account email"
                />
              </div>
              
              <div>
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  placeholder="Enter full name"
                />
              </div>
              
              <div>
                <Label htmlFor="role">Role</Label>
                <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="user">User</SelectItem>
                    <SelectItem value="instructor">Instructor</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Assign Courses</Label>
                <div className="mt-2 space-y-2 max-h-40 overflow-y-auto border rounded p-3">
                  {courses.map((course) => (
                    <div key={course.id} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`course-${course.id}`}
                        checked={formData.courseIds.includes(course.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({...formData, courseIds: [...formData.courseIds, course.id]})
                          } else {
                            setFormData({...formData, courseIds: formData.courseIds.filter(id => id !== course.id)})
                          }
                        }}
                        className="rounded"
                      />
                      <label htmlFor={`course-${course.id}`} className="text-sm">
                        {course.title}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSaveUser}>
                  {editingUser ? 'Update User' : 'Create User'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}