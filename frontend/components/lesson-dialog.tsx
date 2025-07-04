"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { User, ExternalLink, Calendar, X } from "lucide-react"

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
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl">🔗 {lesson.title}</DialogTitle>
            <Button variant="ghost" size="sm" onClick={() => onOpenChange(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Calendar className="w-4 h-4" />
            <span>{lesson.date} - 20:00 - 22:00</span>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Zoom Information */}
          {lesson.zoomLink && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Zoom Meeting:</p>
              <p className="font-mono text-sm">{lesson.zoomLink}</p>
            </div>
          )}

          {/* Instructor Information */}
          {lesson.instructor && (
            <div className="flex items-center space-x-2">
              <User className="w-5 h-5 text-gray-400" />
              <span className="font-medium text-lg">{lesson.instructor}</span>
            </div>
          )}

          {/* Quiz Information */}
          {lesson.quizLink && (
            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm text-gray-600 mb-2">Bài tập: Quiz sau buổi học:</p>
              <a
                href={lesson.quizLink}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm flex items-center space-x-1"
              >
                <span>{lesson.quizLink}</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          )}

          {/* Attachments */}
          {lesson.attachments && lesson.attachments.length > 0 && (
            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm text-gray-600 mb-3">Tài liệu đính kèm:</p>
              <div className="space-y-2">
                {lesson.attachments.map((attachment, index) => (
                  <a
                    key={index}
                    href={attachment.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 text-blue-600 hover:underline text-sm p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                  >
                    <span className="font-medium">{attachment.name}</span>
                    <span className="text-xs text-gray-500">03 Jun 2025</span>
                    <ExternalLink className="w-4 h-4" />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {lesson.description && (
            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm text-gray-600 mb-2">Mô tả:</p>
              <p className="text-sm text-gray-800">{lesson.description}</p>
            </div>
          )}

          {/* Duration */}
          {lesson.duration && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>Thời lượng: {lesson.duration} phút</span>
            </div>
          )}

          {/* Notification */}
          {lesson.notification && (
            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-1">Thông báo</h5>
              <p className="text-sm text-gray-700">{lesson.notification}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between pt-4 border-t">
            {lesson.video_url ? (
              <a
                href={lesson.video_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="default">View recording 🎬</Button>
              </a>
            ) : (
              <Button variant="default" disabled>View recording 🎬</Button>
            )}
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
