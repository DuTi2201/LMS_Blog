"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
// Switch component not available, using checkbox instead
import { Trash2 } from "lucide-react"
import { Course } from "@/lib/api"

interface CourseDialogProps {
  course?: Course | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (courseData: any) => void
  onDelete?: (courseId: string) => void
}

export function CourseDialog({ course, open, onOpenChange, onSave, onDelete }: CourseDialogProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    featured_image: "",
    level: "beginner",
    duration_hours: 0,
    is_published: false
  })

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    if (course) {
      setFormData({
        title: course.title || "",
        description: course.description || "",
        featured_image: course.thumbnail_url || "",
        level: course.difficulty_level || "beginner",
        duration_hours: course.estimated_duration || 0,
        is_published: course.is_published || false
      })
    } else {
      setFormData({
        title: "",
        description: "",
        featured_image: "",
        level: "beginner",
        duration_hours: 0,
        is_published: false
      })
    }
    setShowDeleteConfirm(false)
  }, [course, open])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
    onOpenChange(false)
  }

  const handleDelete = () => {
    if (course && onDelete) {
      onDelete(course.id)
      onOpenChange(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {course ? "Chỉnh sửa khóa học" : "Tạo khóa học mới"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <div>
              <Label htmlFor="title">Tiêu đề khóa học *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Nhập tiêu đề khóa học"
                required
              />
            </div>

            

            <div>
              <Label htmlFor="description">Mô tả chi tiết *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Mô tả chi tiết về nội dung khóa học"
                rows={4}
                required
              />
            </div>

            <div>
              <Label htmlFor="featured_image">Hình ảnh đại diện</Label>
              <Input
                id="featured_image"
                value={formData.featured_image}
                onChange={(e) => setFormData({ ...formData, featured_image: e.target.value })}
                placeholder="URL hình ảnh đại diện"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="level">Cấp độ</Label>
                <Select value={formData.level} onValueChange={(value) => setFormData({ ...formData, level: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Chọn cấp độ" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Cơ bản</SelectItem>
                    <SelectItem value="intermediate">Trung cấp</SelectItem>
                    <SelectItem value="advanced">Nâng cao</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="duration_hours">Thời lượng (giờ)</Label>
                <Input
                  id="duration_hours"
                  type="number"
                  value={formData.duration_hours}
                  onChange={(e) => setFormData({ ...formData, duration_hours: parseInt(e.target.value) || 0 })}
                  placeholder="0"
                  min="0"
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_published"
                checked={formData.is_published}
                onChange={(e) => setFormData({ ...formData, is_published: e.target.checked })}
                className="rounded"
              />
              <Label htmlFor="is_published">Xuất bản khóa học</Label>
            </div>

          </div>

          <DialogFooter className="flex justify-between">
            <div>
              {course && onDelete && (
                <>
                  {!showDeleteConfirm ? (
                    <Button
                      type="button"
                      variant="destructive"
                      onClick={() => setShowDeleteConfirm(true)}
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Xóa khóa học
                    </Button>
                  ) : (
                    <div className="flex space-x-2">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setShowDeleteConfirm(false)}
                      >
                        Hủy
                      </Button>
                      <Button
                        type="button"
                        variant="destructive"
                        onClick={handleDelete}
                      >
                        Xác nhận xóa
                      </Button>
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="flex space-x-2">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Hủy
              </Button>
              <Button type="submit">
                {course ? "Cập nhật" : "Tạo mới"}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}