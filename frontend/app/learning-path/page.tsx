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

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const userData = await apiClient.getCurrentUser()
        setUser(userData)
        
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
    if (!selectedCourse || !currentModuleId) return

    try {
      let savedLesson: Lesson
      
      if (editingLesson) {
        // Update existing lesson
        savedLesson = await apiClient.updateLesson(editingLesson.id, lessonData)
      } else {
        // Create new lesson
        savedLesson = await apiClient.createLesson(currentModuleId, lessonData)
      }

      // Update local state with API response
       const updatedModules = selectedCourse.modules.map(module => {
         if (module.id === currentModuleId) {
           const currentLessons = module.lessons || []
           const updatedLessons = editingLesson
             ? currentLessons.map(lesson =>
                 lesson.id === editingLesson.id ? {
                   ...savedLesson,
                   date: new Date(savedLesson.created_at).toLocaleDateString('en-US', {
                     weekday: 'long',
                     year: 'numeric',
                     month: 'long',
                     day: 'numeric'
                   }),
                   instructor: selectedCourse.instructor?.full_name,
                   zoomLink: undefined,
                   quizLink: undefined,
                   attachments: [],
                   notification: undefined
                 } : lesson
               )
             : [
                 ...currentLessons,
                 {
                   ...savedLesson,
                   date: new Date(savedLesson.created_at).toLocaleDateString('en-US', {
                     weekday: 'long',
                     year: 'numeric',
                     month: 'long',
                     day: 'numeric'
                   }),
                   instructor: selectedCourse.instructor?.full_name,
                   zoomLink: undefined,
                   quizLink: undefined,
                   attachments: [],
                   notification: undefined
                 }
               ]
          
          return { ...module, lessons: updatedLessons }
        }
        return module
      })

      const updatedCourse = { ...selectedCourse, modules: updatedModules }
      setSelectedCourse(updatedCourse)
      setCourses(courses.map(c => c.id === selectedCourse.id ? updatedCourse : c))
      setIsLessonFormDialogOpen(false)
      setCurrentModuleId(null)
    } catch (error) {
      console.error('Failed to save lesson:', error)
      setError('Failed to save lesson')
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
      let savedCourse: Course
      
      if (editingCourse) {
        // Update existing course
        savedCourse = await apiClient.updateCourse(editingCourse.id, courseData)
        const courseWithModules = { ...savedCourse, modules: savedCourse.modules || [] }
        const updatedCourses = courses.map(c => 
          c.id === editingCourse.id ? { ...courseWithModules, modules: c.modules } : c
        )
        setCourses(updatedCourses)
        
        // Update selected course if it's the one being edited
        if (selectedCourse?.id === editingCourse.id) {
          setSelectedCourse({ ...savedCourse, modules: selectedCourse.modules || [] })
        }
      } else {
        // Create new course
        savedCourse = await apiClient.createCourse(courseData)
        const newCourse = { ...savedCourse, modules: savedCourse.modules || [] }
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
            let savedModule: Module
            
            if (editingModule) {
               // Update existing module
               savedModule = await apiClient.updateModule(editingModule.id, {
                 ...moduleData,
                 order_index: editingModule.order_index
               })
             } else {
               // Create new module
               const currentModules = selectedCourse.modules || []
               savedModule = await apiClient.createModule(selectedCourse.id, {
                 ...moduleData,
                 order_index: currentModules.length
               })
             }
 
             // Update local state with API response
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
                   { 
                     ...savedModule, 
                     lessons: [],
                     lessonCount: 0
                   },
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
    </div>
  )
}
