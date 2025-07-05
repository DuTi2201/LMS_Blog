'use client'

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { X, Plus, Trash2 } from "lucide-react"

interface Lesson {
  id: string
  title: string
  description?: string
  instructor?: string
  zoomLink?: string
  quizLink?: string
  attachments?: { name: string; url: string }[]
  notification?: string
  duration?: number
  video_url?: string
}

interface LessonFormDialogProps {
  lesson: Lesson | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (lessonData: any) => void
}

export function LessonFormDialog({ lesson, open, onOpenChange, onSave }: LessonFormDialogProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    instructor: '',
    zoomLink: '',
    quizLink: '',
    notification: '',
    duration: '',
    video_url: '',
    attachments: [] as { name: string; url: string }[]
  })

  useEffect(() => {
    if (lesson) {
      setFormData({
        title: lesson.title || '',
        description: lesson.description || '',
        instructor: lesson.instructor || '',
        zoomLink: lesson.zoomLink || '',
        quizLink: lesson.quizLink || '',
        notification: lesson.notification || '',
        duration: lesson.duration?.toString() || '',
        video_url: lesson.video_url || '',
        attachments: lesson.attachments || []
      })
    } else {
      setFormData({
        title: '',
        description: '',
        instructor: '',
        zoomLink: '',
        quizLink: '',
        notification: '',
        duration: '',
        video_url: '',
        attachments: []
      })
    }
  }, [lesson, open])

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleAddAttachment = () => {
    setFormData(prev => ({
      ...prev,
      attachments: [...prev.attachments, { name: '', url: '' }]
    }))
  }

  const handleRemoveAttachment = (index: number) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }))
  }

  const handleAttachmentChange = (index: number, field: 'name' | 'url', value: string) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.map((attachment, i) => 
        i === index ? { ...attachment, [field]: value } : attachment
      )
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const lessonData = {
      title: formData.title,
      description: formData.description,
      instructor: formData.instructor,
      zoom_link: formData.zoomLink,
      quiz_link: formData.quizLink,
      notification: formData.notification,
      video_url: formData.video_url,
      duration: formData.duration ? parseInt(formData.duration) : undefined,
      order_index: 0, // Default order index
      is_active: true, // Default active state
      attachments: formData.attachments.filter(att => att.name && att.url)
    }
    
    onSave(lessonData)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl">
              {lesson ? 'Edit Lesson' : 'Add New Lesson'}
            </DialogTitle>
            <Button variant="ghost" size="sm" onClick={() => onOpenChange(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Lesson Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter lesson title"
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Enter lesson description"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="instructor">Instructor</Label>
                <Input
                  id="instructor"
                  value={formData.instructor}
                  onChange={(e) => handleInputChange('instructor', e.target.value)}
                  placeholder="Dr. Đình Vinh"
                />
              </div>
              <div>
                <Label htmlFor="duration">Duration (minutes)</Label>
                <Input
                  id="duration"
                  type="number"
                  value={formData.duration}
                  onChange={(e) => handleInputChange('duration', e.target.value)}
                  placeholder="120"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="zoomLink">Zoom Link</Label>
              <Input
                id="zoomLink"
                value={formData.zoomLink}
                onChange={(e) => handleInputChange('zoomLink', e.target.value)}
                placeholder="zoom: 98543998993"
              />
            </div>

            <div>
              <Label htmlFor="quizLink">Quiz Link</Label>
              <Input
                id="quizLink"
                value={formData.quizLink}
                onChange={(e) => handleInputChange('quizLink', e.target.value)}
                placeholder="https://forms.gle/KySZsqsCLfsJRsk86"
              />
            </div>

            <div>
              <Label htmlFor="video_url">Video URL</Label>
              <Input
                id="video_url"
                value={formData.video_url}
                onChange={(e) => handleInputChange('video_url', e.target.value)}
                placeholder="https://example.com/video.mp4"
              />
            </div>

            <div>
              <Label htmlFor="notification">Notification</Label>
              <Textarea
                id="notification"
                value={formData.notification}
                onChange={(e) => handleInputChange('notification', e.target.value)}
                placeholder="Deadline Recording: 30/06/2025"
                rows={2}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-3">
                <Label>Attachments</Label>
                <Button type="button" variant="outline" size="sm" onClick={handleAddAttachment}>
                  <Plus className="w-4 h-4 mr-1" />
                  Add Attachment
                </Button>
              </div>
              
              {formData.attachments.map((attachment, index) => (
                <div key={index} className="flex items-center space-x-2 mb-2">
                  <Input
                    placeholder="Attachment name"
                    value={attachment.name}
                    onChange={(e) => handleAttachmentChange(index, 'name', e.target.value)}
                    className="flex-1"
                  />
                  <Input
                    placeholder="Attachment URL"
                    value={attachment.url}
                    onChange={(e) => handleAttachmentChange(index, 'url', e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveAttachment(index)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">
              {lesson ? 'Update Lesson' : 'Create Lesson'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}