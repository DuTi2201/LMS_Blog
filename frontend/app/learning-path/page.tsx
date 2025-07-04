"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronDown, ChevronUp, Plus, Edit, Trash2, Calendar, Loader2, Trophy } from "lucide-react"
import { LessonDialog } from "@/components/lesson-dialog"
import { LessonFormDialog } from "@/components/lesson-form-dialog"
import { ModuleDialog } from "@/components/module-dialog"
import { CourseDialog } from "@/components/course-dialog"
import { LoginDialog } from "@/components/login-dialog"
import { apiClient } from "@/lib/api"
import type { Course as ApiCourse, Module as ApiModule, Lesson as ApiLesson, User } from "@/lib/api"

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

interface LessonFormData {
  title: string
  description?: string
  instructor?: string
  zoom_link?: string
  quiz_link?: string
  notification?: string
}

export default function LearningPathPage() {
  const [user, setUser] = useState<User | null>(null)
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set())
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null)
  const [isLessonDialogOpen, setIsLessonDialogOpen] = useState(false)
  const [editingModule, setEditingModule] = useState<Module | null>(null)
  const [isModuleDialogOpen, setIsModuleDialogOpen] = useState(false)
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null)
  const [isLessonFormDialogOpen, setIsLessonFormDialogOpen] = useState(false)
  const [currentModuleId, setCurrentModuleId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingCourse, setEditingCourse] = useState<Course | null>(null)
  const [isCourseDialogOpen, setIsCourseDialogOpen] = useState(false)
  const [isLoginDialogOpen, setIsLoginDialogOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const checkAuthAndFetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Check if user is authenticated
        if (!apiClient.isAuthenticated()) {
          setIsAuthenticated(false)
          setIsLoginDialogOpen(true)
          setLoading(false)
          return
        }
        
        const userData = await apiClient.getCurrentUser()
        setUser(userData)
        setIsAuthenticated(true)
        
        // Fetch courses based on user role
        let coursesData: any[]
        if (userData.role === 'admin') {
          // Admin can see all courses
          coursesData = await apiClient.getCourses(0, 100)
        } else {
          // Other roles can only see enrolled courses
          coursesData = await apiClient.getEnrolledCourses(0, 100)
        }
        
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
                  instructor: lesson.instructor || course.instructor?.full_name,
                  zoomLink: lesson.zoom_link,
                  quizLink: lesson.quiz_link,
                  attachments: lesson.attachments || [],
                  notification: lesson.notification
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
        if (err instanceof Error && (err.message.includes('Authentication required') || err.message.includes('Session expired'))) {
          setIsAuthenticated(false)
          setIsLoginDialogOpen(true)
        } else {
          setError('Failed to load data')
        }
      } finally {
        setLoading(false)
      }
    }

    checkAuthAndFetchData()
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
      await apiClient.deleteModule(moduleId)
      
      // Update local state after successful API call
      const updatedCourse = {
        ...selectedCourse,
        modules: selectedCourse.modules.filter((m) => m.id !== moduleId)
      }
      setSelectedCourse(updatedCourse)
      setCourses(courses.map(c => c.id === selectedCourse.id ? updatedCourse : c))
    } catch (error) {
      console.error('Failed to delete module:', error)
      setError('Failed to delete module')
    }
  }

  const handleAddLesson = (moduleId: string) => {
    setCurrentModuleId(moduleId)
    setEditingLesson(null)
    setIsLessonFormDialogOpen(true)
  }

  const handleEditLesson = (lesson: Lesson) => {
    setEditingLesson(lesson)
    setCurrentModuleId(lesson.module_id)
    setIsLessonFormDialogOpen(true)
  }

  const handleDeleteLesson = async (lessonId: string, moduleId: string) => {
    if (!selectedCourse) return
    
    try {
      await apiClient.deleteLesson(lessonId)
      
      // Update local state after successful API call
      const updatedModules = selectedCourse.modules.map(module => {
        if (module.id === moduleId) {
          return {
            ...module,
            lessons: module.lessons.filter(lesson => lesson.id !== lessonId)
          }
        }
        return module
      })
      
      const updatedCourse = { ...selectedCourse, modules: updatedModules }
      setSelectedCourse(updatedCourse)
      setCourses(courses.map(c => c.id === selectedCourse.id ? updatedCourse : c))
    } catch (error) {
      console.error('Failed to delete lesson:', error)
      setError('Failed to delete lesson')
    }
  }

  const handleSaveLesson = async (lessonData: any) => {
    if (!selectedCourse || !currentModuleId) {
      setError('No course or module selected')
      return
    }

    // Validate required fields
    if (!lessonData.title?.trim()) {
      setError('Lesson title is required')
      return
    }

    try {
      // Calculate order for new lessons
      const currentModule = selectedCourse.modules?.find(m => m.id === currentModuleId)
      const order_index = editingLesson ? editingLesson.order_index : (currentModule?.lessons?.length || 0) + 1

      // Transform frontend lesson data to backend format (matching database schema)
      const backendLessonData = {
        title: lessonData.title.trim(),
        description: lessonData.description?.trim() || undefined,
        instructor: lessonData.instructor?.trim() || undefined,
        zoom_link: lessonData.zoom_link?.trim() || undefined,
        quiz_link: lessonData.quiz_link?.trim() || undefined,
        video_url: lessonData.video_url?.trim() || undefined,
        duration: lessonData.duration ? parseInt(lessonData.duration) : undefined,
        notification: lessonData.notification?.trim() || undefined,
        order_index: order_index,
        attachments: lessonData.attachments || []
      }
      
      let apiLesson: ApiLesson  
      
      if (editingLesson) {
        // Update existing lesson
        apiLesson = await apiClient.updateLesson(editingLesson.id, backendLessonData)
      } else {
        // Create new lesson
        apiLesson = await apiClient.createLesson(currentModuleId, backendLessonData)
      }
      
      // Transform API lesson to UI lesson
      const savedLesson: Lesson = {
        ...apiLesson,
        date: new Date(apiLesson.created_at).toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }),
        instructor: apiLesson.instructor || selectedCourse.instructor?.full_name,
        zoomLink: apiLesson.zoom_link,
        quizLink: apiLesson.quiz_link,
        attachments: apiLesson.attachments || [],
        notification: apiLesson.notification
      }

      // Update local state with transformed lesson
      const updatedModules = selectedCourse.modules?.map(module => {
        if (module.id === currentModuleId) {
           const currentLessons = module.lessons || []
           const updatedLessons = editingLesson
             ? currentLessons.map(lesson =>
                 lesson.id === editingLesson.id ? savedLesson : lesson
               )
             : [...currentLessons, savedLesson]
          
          return { 
            ...module, 
            lessons: updatedLessons,
            lessonCount: updatedLessons.length
          }
        }
        return module
      }) || []

      const updatedCourse = { ...selectedCourse, modules: updatedModules }
      setSelectedCourse(updatedCourse)
      setCourses(courses.map(c => c.id === selectedCourse.id ? updatedCourse : c))
      
      // Reset form state
      setIsLessonFormDialogOpen(false)
      setEditingLesson(null)
      setCurrentModuleId(null)
      setError(null)
    } catch (error) {
      console.error('Failed to save lesson:', error)
      setError(error instanceof Error ? error.message : 'Failed to save lesson')
    }
  }

  const handleAddCourse = () => {
    setEditingCourse(null)
    setIsCourseDialogOpen(true)
  }

  const handleEditCourse = (course: Course) => {
    setEditingCourse(course)
    setIsCourseDialogOpen(true)
  }

  const handleDeleteCourse = async (courseId: string) => {
    try {
      await apiClient.deleteCourse(courseId)
      
      // Update local state
      const updatedCourses = courses.filter(c => c.id !== courseId)
      setCourses(updatedCourses)
      
      // If deleted course was selected, select first available course
      if (selectedCourse?.id === courseId) {
        setSelectedCourse(updatedCourses[0] || null)
      }
    } catch (error) {
      console.error('Failed to delete course:', error)
      setError('Failed to delete course')
    }
  }

  const handleSaveCourse = async (courseData: any) => {
    try {
      let apiCourse: ApiCourse
      
      if (editingCourse) {
        // Update existing course
        apiCourse = await apiClient.updateCourse(editingCourse.id, courseData)
        const transformedModules: Module[] = (apiCourse.modules || []).map(module => ({
          ...module,
          lessons: [],
          lessonCount: 0
        }))
        const savedCourse: Course = { ...apiCourse, modules: transformedModules }
        const updatedCourses = courses.map(c => 
          c.id === editingCourse.id ? { ...savedCourse, modules: c.modules } : c
        )
        setCourses(updatedCourses)
        
        // Update selected course if it's the one being edited
        if (selectedCourse?.id === editingCourse.id) {
          setSelectedCourse({ ...savedCourse, modules: selectedCourse.modules || [] })
        }
      } else {
        // Create new course
        apiCourse = await apiClient.createCourse(courseData)
        const transformedModules: Module[] = (apiCourse.modules || []).map(module => ({
          ...module,
          lessons: [],
          lessonCount: 0
        }))
        const newCourse: Course = { ...apiCourse, modules: transformedModules }
        setCourses([...courses, newCourse])
        
        // Select the new course if no course is currently selected
        if (!selectedCourse) {
          setSelectedCourse(newCourse)
        }
      }
      
      setIsCourseDialogOpen(false)
    } catch (error) {
      console.error('Failed to save course:', error)
      setError('Failed to save course')
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

  const handleLogin = (userData: User) => {
    setUser(userData)
    setIsAuthenticated(true)
    setIsLoginDialogOpen(false)
    // Reload the page data after successful login
    window.location.reload()
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
        <LoginDialog
          open={isLoginDialogOpen}
          onOpenChange={setIsLoginDialogOpen}
          onLogin={handleLogin}
        />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Authentication Required</h2>
              <p className="text-gray-600 mb-4">Please log in to access the learning path.</p>
              <Button onClick={() => setIsLoginDialogOpen(true)}>Login</Button>
            </div>
          </div>
        </div>
        <LoginDialog
          open={isLoginDialogOpen}
          onOpenChange={setIsLoginDialogOpen}
          onLogin={handleLogin}
        />
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
            <div className="text-gray-600 mb-4">
              {user?.role === 'admin' 
                ? 'No courses available' 
                : 'Chưa có khoá học nào dành cho bạn'
              }
            </div>
            {user?.role === 'admin' && (
              <Button onClick={handleAddCourse}>
                <Plus className="w-4 h-4 mr-2" />
                Tạo khóa học đầu tiên
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
                  <SelectItem key={course.id} value={course.id}>
                    {course.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {user?.role === "admin" && (
              <>
                {selectedCourse && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEditCourse(selectedCourse)}
                    title="Chỉnh sửa khóa học hiện tại"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                )}
                <Button onClick={handleAddCourse} title="Thêm khóa học mới">
                  <Plus className="w-4 h-4 mr-2" />
                  Thêm khóa học
                </Button>
              </>
            )}
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{selectedCourse.title}</h2>
          <p className="text-gray-600">{selectedCourse.description}</p>
        </div>

        <div className="space-y-4">
          {user?.role === "admin" && (
            <Button onClick={handleAddModule}>
              <Plus className="w-4 h-4 mr-2" />
              Add Module
            </Button>
          )}
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
                          <Button variant="ghost" size="sm" onClick={() => handleAddLesson(module.id)} title="Add Lesson">
                            <Plus className="w-4 h-4" />
                          </Button>
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
                          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          <div 
                            className="flex-1 cursor-pointer"
                            onClick={() => openLessonDialog(lesson)}
                          >
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium text-gray-900">{lesson.title}</h4>
                              {user?.role === "admin" && (
                                <div className="flex space-x-1" onClick={(e) => e.stopPropagation()}>
                                  <Button variant="ghost" size="sm" onClick={() => handleEditLesson(lesson)} title="Edit Lesson">
                                    <Edit className="w-3 h-3" />
                                  </Button>
                                  <Button variant="ghost" size="sm" onClick={() => handleDeleteLesson(lesson.id, module.id)} title="Delete Lesson">
                                    <Trash2 className="w-3 h-3" />
                                  </Button>
                                </div>
                              )}
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                              <div className="flex items-center space-x-1">
                                <Calendar className="w-4 h-4" />
                                <span>{lesson.date || formatDate(lesson.created_at)}</span>
                              </div>
                              {lesson.instructor && (
                                <span className="text-purple-600">👨‍🏫 {lesson.instructor}</span>
                              )}
                              {lesson.video_url && (
                                <span className="text-blue-600">📹 Video Available</span>
                              )}
                              {lesson.duration && (
                                <span className="text-green-600">⏱️ {lesson.duration} min</span>
                              )}
                            </div>
                            <div className="mt-2 text-sm text-gray-600">
                              {lesson.quizLink && (
                                <span className="text-orange-600">📝 Quiz Available</span>
                              )}
                              {lesson.attachments && lesson.attachments.length > 0 && (
                                <span className="text-blue-600 ml-2">📎 {lesson.attachments.length} attachment(s)</span>
                              )}
                              {lesson.notification && (
                                <span className="text-yellow-600 ml-2">🔔 Notification</span>
                              )}
                            </div>
                          </div>
                          <Badge variant="outline" className="text-xs ml-2">
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

      <LessonFormDialog
        lesson={editingLesson}
        open={isLessonFormDialogOpen}
        onOpenChange={setIsLessonFormDialogOpen}
        onSave={handleSaveLesson}
      />

      <ModuleDialog
        module={editingModule}
        open={isModuleDialogOpen}
        onOpenChange={setIsModuleDialogOpen}
        onSave={async (moduleData) => {
          if (!selectedCourse) return

          try {
            let apiModule: any
            
            if (editingModule) {
              // Update existing module
              apiModule = await apiClient.updateModule(editingModule.id, {
                ...moduleData,
                order_index: editingModule.order_index
              })
            } else {
              // Create new module
              const currentModules = selectedCourse.modules || []
              apiModule = await apiClient.createModule(selectedCourse.id, {
                ...moduleData,
                order_index: currentModules.length
              })
            }

            // Transform API response to local Module type
            const savedModule: Module = {
              ...apiModule,
              lessons: [],
              lessonCount: 0
            }
 
            // Update local state with transformed module
            const currentModules = selectedCourse.modules || []
            const updatedModules = editingModule
              ? currentModules.map((m) =>
                  m.id === editingModule.id ? { 
                    ...savedModule, 
                    lessons: m.lessons || [], 
                    lessonCount: m.lessons?.length || 0 
                  } : m
                )
              : [
                  ...currentModules,
                  savedModule,
                ]

            const updatedCourse = { ...selectedCourse, modules: updatedModules }
            setCourses(courses.map((c) => (c.id === updatedCourse.id ? updatedCourse : c)))
            setSelectedCourse(updatedCourse)
            setIsModuleDialogOpen(false)
          } catch (error) {
            console.error('Failed to save module:', error)
            setError('Failed to save module')
          }
        }}
      />

      <CourseDialog
        course={editingCourse}
        open={isCourseDialogOpen}
        onOpenChange={setIsCourseDialogOpen}
        onSave={handleSaveCourse}
        onDelete={handleDeleteCourse}
      />

      <LoginDialog
        open={isLoginDialogOpen}
        onOpenChange={setIsLoginDialogOpen}
        onLogin={handleLogin}
      />
    </div>
  )
}
