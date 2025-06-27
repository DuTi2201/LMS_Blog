"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, User, ExternalLink, X } from "lucide-react"

interface Lesson {
  id: string
  title: string
  date: string
  instructor?: string
  zoomLink?: string
  quizLink?: string
  attachments?: { name: string; url: string }[]
  notification?: string
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
          {lesson.zoomLink && (
            <div>
              <p className="text-sm text-gray-600">zoom: {lesson.zoomLink.split("/").pop()}</p>
            </div>
          )}

          <div className="border-t border-gray-200 pt-4">
            <p className="text-sm text-gray-600 mb-2">Quiz sau buổi học:</p>
            {lesson.quizLink && (
              <a
                href={lesson.quizLink}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                {lesson.quizLink}
              </a>
            )}
          </div>

          {lesson.instructor && (
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4 text-gray-400" />
              <span className="font-medium">{lesson.instructor}</span>
            </div>
          )}

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">{lesson.title}</h4>
            <div className="flex items-center space-x-2 text-sm text-gray-500 mb-3">
              <span>zoom: {lesson.zoomLink?.split("/").pop()}</span>
            </div>

            <div className="border-t border-gray-200 pt-3 mt-3">
              <p className="text-sm text-gray-600 mb-2">Quiz sau buổi học:</p>
              {lesson.quizLink && (
                <a
                  href={lesson.quizLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline text-sm flex items-center space-x-1"
                >
                  <span>{lesson.quizLink}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>

            {lesson.attachments && lesson.attachments.length > 0 && (
              <div className="mt-4">
                {lesson.attachments.map((attachment, index) => (
                  <a
                    key={index}
                    href={attachment.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 text-blue-600 hover:underline text-sm"
                  >
                    <span>{attachment.name}</span>
                    <span className="text-xs text-gray-500">03 Jun 2025</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                ))}
              </div>
            )}

            <Badge className="mt-3">2025</Badge>
          </div>

          {lesson.notification && (
            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-1">Notification</h5>
              <p className="text-sm text-gray-700">{lesson.notification}</p>
            </div>
          )}

          <div className="flex justify-between">
            <Button variant="default">View recording 🎬</Button>
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
