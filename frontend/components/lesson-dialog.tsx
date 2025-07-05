"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { User, ExternalLink, Calendar, X, Clock, FileText, Video, Bell } from "lucide-react"

interface Lesson {
  id: string
  title: string
  date?: string
  created_at?: string
  instructor?: string
  zoomLink?: string
  quizLink?: string
  attachments?: { name: string; url: string }[]
  notification?: string
  video_url?: string
  duration?: number
  description?: string
}

interface LessonDialogProps {
  lesson: Lesson | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function LessonDialog({ lesson, open, onOpenChange }: LessonDialogProps) {
  if (!lesson) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader className="pb-4 border-b">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-2xl font-bold text-gray-900 mb-2 pr-8">
                {lesson.title}
              </DialogTitle>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-4 h-4" />
                  <span>{lesson.date || lesson.created_at} - 20:00 - 22:00</span>
                </div>
                {lesson.duration && (
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{lesson.duration} phút</span>
                  </div>
                )}
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={() => onOpenChange(false)} className="shrink-0">
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Instructor Information */}
          {lesson.instructor && (
            <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Giảng viên</p>
                <p className="font-semibold text-gray-900">{lesson.instructor}</p>
              </div>
            </div>
          )}

          {/* Description */}
          {lesson.description && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-gray-500" />
                <h4 className="font-medium text-gray-900">Mô tả bài học</h4>
              </div>
              <p className="text-gray-700 leading-relaxed pl-6">{lesson.description}</p>
            </div>
          )}

          {/* Zoom Information */}
          {lesson.zoomLink && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Video className="w-4 h-4 text-green-600" />
                <h4 className="font-medium text-gray-900">Zoom Meeting</h4>
              </div>
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg ml-6">
                <p className="font-mono text-sm text-green-800 break-all">{lesson.zoomLink}</p>
              </div>
            </div>
          )}

          {/* Quiz Information */}
          {lesson.quizLink && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-orange-600" />
                <h4 className="font-medium text-gray-900">Quiz sau buổi học</h4>
              </div>
              <div className="ml-6">
                <a
                  href={lesson.quizLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-800 hover:underline transition-colors p-3 bg-blue-50 rounded-lg border border-blue-200 hover:border-blue-300"
                >
                  <span className="text-sm font-medium">Làm bài quiz</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          )}

          {/* Attachments */}
          {lesson.attachments && lesson.attachments.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-purple-600" />
                <h4 className="font-medium text-gray-900">Tài liệu đính kèm</h4>
                <Badge variant="secondary" className="text-xs">{lesson.attachments.length}</Badge>
              </div>
              <div className="space-y-2 ml-6">
                {lesson.attachments.map((attachment, index) => (
                  <a
                    key={index}
                    href={attachment.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-3 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 hover:border-purple-300 transition-colors group"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center">
                        <FileText className="w-4 h-4 text-purple-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">{attachment.name}</p>
                        <p className="text-xs text-gray-500">03 Jun 2025</p>
                      </div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-purple-600 group-hover:text-purple-800" />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Notification */}
          {lesson.notification && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Bell className="w-4 h-4 text-yellow-600" />
                <h4 className="font-medium text-gray-900">Thông báo</h4>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg ml-6">
                <p className="text-sm text-yellow-800 leading-relaxed">{lesson.notification}</p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between items-center pt-6 border-t border-gray-200">
            {lesson.video_url ? (
              <a
                href={lesson.video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 mr-3"
              >
                <Button variant="default" className="w-full flex items-center space-x-2">
                  <Video className="w-4 h-4" />
                  <span>View recording</span>
                </Button>
              </a>
            ) : (
              <Button variant="default" disabled className="flex-1 mr-3 flex items-center space-x-2">
                <Video className="w-4 h-4" />
                <span>View recording</span>
              </Button>
            )}
            <Button variant="outline" onClick={() => onOpenChange(false)} className="px-6">
              Đóng
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
