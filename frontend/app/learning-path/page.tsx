"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronUp, Calendar, Trophy, Plus, Edit, Trash2, Loader2 } from "lucide-react"
import { LessonDialog } from "@/components/lesson-dialog"
import { ModuleDialog } from "@/components/module-dialog"
import { apiClient } from "@/lib/api"

interface Lesson {
  id: number
  title: string
  content: string
  video_url?: string
  attachments?: string[]
  order_index: number
  created_at: string
  updated_at: string
}

interface Module {
  id: number
  title: string
  description: string
  order_index: number
  lessons: Lesson[]
  created_at: string
  updated_at: string
}

interface Course {
  id: number
  title: string
  description: string
  modules: Module[]
  created_at: string
  updated_at: string
}

export default function LearningPathPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
  const [expandedModules, setExpandedModules] = useState<Set<number>>(new Set())
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null)
  const [isLessonDialogOpen, setIsLessonDialogOpen] = useState(false)
  const [isModuleDialogOpen, setIsModuleDialogOpen] = useState(false)
  const [editingModule, setEditingModule] = useState<Module | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Check if user is authenticated
        const token = localStorage.getItem('access_token')
        if (token) {
          const userData = await apiClient.getCurrentUser()
          setUser(userData)
        }
        
        // Fetch courses
        const coursesData = await apiClient.getCourses()
        setCourses(coursesData)
        
        // Select first course by default
        if (coursesData.length > 0) {
          setSelectedCourse(coursesData[0])
          // Expand first module by default
          if (coursesData[0].modules.length > 0) {
            setExpandedModules(new Set([coursesData[0].modules[0].id]))
          }
        }
      } catch (error: any) {
        console.error('Failed to fetch learning data:', error)
        setError(error.message || 'Failed to load learning path')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const toggleModule = (moduleId: number) => {
    const newExpanded = new Set(expandedModules)
    if (newExpanded.has(moduleId)) {
      newExpanded.delete(moduleId)
    } else {
      newExpanded.add(moduleId)
    }
    setExpandedModules(newExpanded)
  }

  const openLessonDialog = (lesson: Lesson) => {
    setSelectedLesson(lesson)
    setIsLessonDialogOpen(true)
  }

  const handleAddModule = () => {
    setEditingModule(null)
    setIsModuleDialogOpen(true)
  }

  const handleEditModule = (module: Module) => {
    setEditingModule(module)
    setIsModuleDialogOpen(true)
  }

  const handleDeleteModule = async (moduleId: number) => {
    if (!selectedCourse) return
    
    try {
      // Note: Implement delete module API call when available
      // await apiClient.deleteModule(moduleId)
      
      // Update local state
      const updatedCourse = {
        ...selectedCourse,
        modules: selectedCourse.modules.filter((m) => m.id !== moduleId)
      }
      setSelectedCourse(updatedCourse)
      setCourses(courses.map(c => c.id === selectedCourse.id ? updatedCourse : c))
    } catch (error: any) {
      console.error('Failed to delete module:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin" />
            <span className="ml-2">Loading learning path...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="text-red-600 mb-4">{error}</div>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </div>
        </div>
      </div>
    )
  }

  if (!selectedCourse) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="text-gray-600 mb-4">No courses available</div>
            {user?.role === 'admin' && (
              <Button onClick={handleAddModule}>
                <Plus className="w-4 h-4 mr-2" />
                Create First Course
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Notification Banner */}
      <div className="bg-green-600 text-white">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Trophy className="w-5 h-5" />
              <span>🏆 AIO2025 Exam (Thứ hệ thống) One or more contests are available for you to participate in</span>
            </div>
            <Button variant="outline" size="sm" className="text-green-600 bg-white hover:bg-gray-100">
              Take a look →
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <h1 className="text-3xl font-bold text-gray-900">Learning Path</h1>
            <Trophy className="w-6 h-6 text-yellow-500" />
          </div>

          <div className="flex items-center space-x-4">
            <select 
              className="px-4 py-2 border border-gray-300 rounded-lg bg-white"
              value={selectedCourse?.id || ''}
              onChange={(e) => {
                const courseId = parseInt(e.target.value)
                const course = courses.find(c => c.id === courseId)
                if (course) {
                  setSelectedCourse(course)
                  setExpandedModules(new Set())
                }
              }}
            >
              {courses.map(course => (
                <option key={course.id} value={course.id}>{course.title}</option>
              ))}
            </select>
            {user?.role === "admin" && (
              <Button onClick={handleAddModule}>
                <Plus className="w-4 h-4 mr-2" />
                Add Module
              </Button>
            )}
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{selectedCourse.title}</h2>
          <p className="text-gray-600">{selectedCourse.description}</p>
        </div>

        <div className="space-y-4">
          {selectedCourse.modules.map((module) => (
            <Card key={module.id} className="overflow-hidden">
              <CardHeader
                className="cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => toggleModule(module.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <CardTitle className="text-xl text-gray-900">{module.title}</CardTitle>
                      <Badge variant="secondary">{module.lessons.length} lessons</Badge>
                      {user?.role === "admin" && (
                        <div className="flex space-x-2" onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="sm" onClick={() => handleEditModule(module)}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteModule(module.id)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                    <p className="text-gray-600 mt-2">{module.description}</p>
                  </div>
                  {expandedModules.has(module.id) ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </CardHeader>

              {expandedModules.has(module.id) && (
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {module.lessons.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        No lessons available in this module
                      </div>
                    ) : (
                      module.lessons.map((lesson) => (
                        <div
                          key={lesson.id}
                          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                          onClick={() => openLessonDialog(lesson)}
                        >
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">{lesson.title}</h4>
                            <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                              <div className="flex items-center space-x-1">
                                <Calendar className="w-4 h-4" />
                                <span>{formatDate(lesson.created_at)}</span>
                              </div>
                              {lesson.video_url && (
                                <span className="text-blue-600">Video Available</span>
                              )}
                              {lesson.attachments && lesson.attachments.length > 0 && (
                                <span className="text-green-600">{lesson.attachments.length} attachments</span>
                              )}
                            </div>
                            <div className="mt-2 text-sm text-gray-600 line-clamp-2">
                              {lesson.content}
                            </div>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            Lesson {lesson.order_index}
                          </Badge>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      </div>

      <LessonDialog lesson={selectedLesson} open={isLessonDialogOpen} onOpenChange={setIsLessonDialogOpen} />

      <ModuleDialog
        module={editingModule}
        open={isModuleDialogOpen}
        onOpenChange={setIsModuleDialogOpen}
        onSave={(moduleData) => {
          if (editingModule) {
            setModules(modules.map((m) => (m.id === editingModule.id ? { ...m, ...moduleData } : m)))
          } else {
            const newModule: Module = {
              id: Date.now().toString(),
              lessons: [],
              ...moduleData,
            }
            setModules([...modules, newModule])
          }
        }}
      />
    </div>
  )
}
