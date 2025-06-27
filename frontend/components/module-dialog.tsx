"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

interface Module {
  id: string
  title: string
  description: string
  lessonCount: number
}

interface ModuleDialogProps {
  module: Module | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (moduleData: Omit<Module, "id" | "lessons">) => void
}

export function ModuleDialog({ module, open, onOpenChange, onSave }: ModuleDialogProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [lessonCount, setLessonCount] = useState(0)

  useEffect(() => {
    if (module) {
      setTitle(module.title)
      setDescription(module.description)
      setLessonCount(module.lessonCount)
    } else {
      setTitle("")
      setDescription("")
      setLessonCount(0)
    }
  }, [module])

  const handleSave = () => {
    onSave({
      title,
      description,
      lessonCount,
    })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{module ? "Edit Module" : "Add New Module"}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label htmlFor="title">Module Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Module 1 - Fundamental Math and Programming"
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what this module covers..."
              rows={3}
            />
          </div>

          <div>
            <Label htmlFor="lessonCount">Number of Lessons</Label>
            <Input
              id="lessonCount"
              type="number"
              value={lessonCount}
              onChange={(e) => setLessonCount(Number.parseInt(e.target.value) || 0)}
              min="0"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>{module ? "Update" : "Create"}</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
