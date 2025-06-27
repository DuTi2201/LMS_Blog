"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronDown, ChevronUp, Plus, Edit, Trash2, Calendar, Loader2, Trophy } from "lucide-react"
import { LessonDialog } from "@/components/lesson-dialog"
import { ModuleDialog } from "@/components/module-dialog"
import { apiClient } from "@/lib/api"
import type { Course as ApiCourse, Module as ApiModule, Lesson as ApiLesson, User as ApiUser } from "@/lib/api"

// Extended types for UI components
interface Course extends ApiCourse {
  modules: Module[]
}

interface Module extends ApiModule {
  lessons: Lesson[]
  lessonCount: number
}

interface Lesson extends ApiLesson {
  date: string
  instructor?: string
  zoomLink?: string
  quizLink?: string
  attachments?: { name: string; url: string }[]
  notification?: string
}

export default function LearningPathPage() {
  const [user, setUser] = useState<ApiUser | null>(null)
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set())
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null)
  const [isLessonDialogOpen, setIsLessonDialogOpen] = useState(false)
  const [editingModule, setEditingModule] = useState<Module | null>(null)
  const [isModuleDialogOpen, setIsModuleDialogOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [userData, coursesData] = await Promise.all([
          apiClient.getCurrentUser(),
          apiClient.getCourses()
        ])
        setUser(userData as ApiUser)
        
        // Transform courses data to include modules with lessons
        const coursesWithModules = await Promise.all(
          coursesData.map(async (course) => {
            const modules = await apiClient.getModules(course.id)
            const modulesWithLessons = await Promise.all(
              modules.map(async (module) => {
                const lessons = await apiClient.getLessons(module.id)
                const transformedLessons = lessons?.map(lesson => ({
                  ...lesson,
                  date: lesson.created_at,
                  instructor: course.instructor?.full_name,
                  zoomLink: undefined,
                  quizLink: undefined,
                  attachments: [],
                  notification: undefined
                })) || []
                return {
                  ...module,
                  lessons: transformedLessons,
                  lessonCount: transformedLessons.length
                }
              })
            )
            return {
              ...course,
              modules: modulesWithLessons
            }
          })
        )
        
        setCourses(coursesWithModules)
        setSelectedCourse(coursesWithModules[0] || null)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const toggleModule = (moduleId: string) => {
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

  const handleDeleteModule = async (moduleId: string) => {
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
    } catch (error) {
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
            <Select value={selectedCourse?.id || ""} onValueChange={(courseId) => {
              const course = courses.find(c => c.id === courseId)
              setSelectedCourse(course || null)
            }}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select a course" />
              </SelectTrigger>
              <SelectContent>
              {courses.map(course => (
                   <SelectItem key={course.id} value={course.id}>{course.title}</SelectItem>
                 ))}
               </SelectContent>
             </Select>
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
          {selectedCourse.modules?.map((module) => (
            <Card key={module.id} className="overflow-hidden">
              <CardHeader
                className="cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => toggleModule(module.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <CardTitle className="text-xl text-gray-900">{module.title}</CardTitle>
                      <Badge variant="secondary">{module.lessons?.length || 0} lessons</Badge>
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
                    {(!module.lessons || module.lessons.length === 0) ? (
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
                              {lesson.duration && (
                                <span className="text-green-600">{lesson.duration} min</span>
                              )}
                            </div>
                            <div className="mt-2 text-sm text-gray-600 line-clamp-2">
                              {lesson.lesson_type && `Type: ${lesson.lesson_type}`}
                            </div>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            Lesson
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
          if (!selectedCourse) return

          const currentModules = selectedCourse.modules || []
          const updatedModules = editingModule
            ? currentModules.map((m) =>
                m.id === editingModule.id ? { ...m, ...moduleData } : m
              )
            : [
                ...currentModules,
                { 
                  ...moduleData, 
                  id: Date.now().toString(), 
                  lessons: [],
                  lessonCount: 0,
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                  course_id: selectedCourse.id,
                  order_index: currentModules.length
                },
              ]

          const updatedCourse = { ...selectedCourse, modules: updatedModules }
          setCourses(courses.map((c) => (c.id === updatedCourse.id ? updatedCourse : c)))
          setSelectedCourse(updatedCourse)
        }}
      />
    </div>
  )
}
