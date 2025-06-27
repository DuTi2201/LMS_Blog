"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { X, Loader2 } from "lucide-react"
import { apiClient } from "@/lib/api-client"

interface BlogPost {
  id: number
  title: string
  content: string
  author: {
    id: number
    full_name: string
    email: string
  }
  created_at: string
  updated_at: string
  tags: {
    id: number
    name: string
  }[]
  category: {
    id: number
    name: string
  }
  is_published: boolean
  word_count: number
}

interface Category {
  id: number
  name: string
}

interface Tag {
  id: number
  name: string
}

interface BlogEditorProps {
  post: BlogPost | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (postData: any) => void
}

export function BlogEditor({ post, open, onOpenChange, onSave }: BlogEditorProps) {
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [selectedTags, setSelectedTags] = useState<number[]>([])
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)
  const [isPublished, setIsPublished] = useState(false)
  const [newTag, setNewTag] = useState("")
  const [categories, setCategories] = useState<Category[]>([])
  const [availableTags, setAvailableTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(false)
  const [dataLoading, setDataLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setDataLoading(true)
        const [categoriesData, tagsData] = await Promise.all([
          apiClient.getBlogCategories(),
          apiClient.getBlogTags()
        ])
        setCategories(categoriesData)
        setAvailableTags(tagsData)
      } catch (err) {
        console.error('Error fetching categories and tags:', err)
      } finally {
        setDataLoading(false)
      }
    }

    if (open) {
      fetchData()
    }
  }, [open])

  useEffect(() => {
    if (post) {
      setTitle(post.title)
      setContent(post.content)
      setSelectedTags(post.tags.map(tag => tag.id))
      setSelectedCategory(post.category.id)
      setIsPublished(post.is_published)
    } else {
      setTitle("")
      setContent("")
      setSelectedTags([])
      setSelectedCategory(null)
      setIsPublished(false)
    }
  }, [post])

  const addTag = async () => {
    if (newTag.trim()) {
      try {
        // Check if tag already exists
        const existingTag = availableTags.find(tag => tag.name.toLowerCase() === newTag.trim().toLowerCase())
        if (existingTag) {
          if (!selectedTags.includes(existingTag.id)) {
            setSelectedTags([...selectedTags, existingTag.id])
          }
        } else {
          // Create new tag
          const newTagData = await apiClient.createBlogTag({ name: newTag.trim() })
          setAvailableTags([...availableTags, newTagData])
          setSelectedTags([...selectedTags, newTagData.id])
        }
        setNewTag("")
      } catch (err) {
        console.error('Error adding tag:', err)
      }
    }
  }

  const removeTag = (tagId: number) => {
    setSelectedTags(selectedTags.filter((id) => id !== tagId))
  }

  const toggleTag = (tagId: number) => {
    if (selectedTags.includes(tagId)) {
      removeTag(tagId)
    } else {
      setSelectedTags([...selectedTags, tagId])
    }
  }

  const calculateReadTime = (text: string) => {
    const wordsPerMinute = 200
    const wordCount = text.split(/\s+/).length
    const minutes = Math.ceil(wordCount / wordsPerMinute)
    return `${minutes} minutes`
  }

  const handleSave = async () => {
    if (!title.trim() || !content.trim() || !selectedCategory) {
      alert('Please fill in all required fields')
      return
    }

    setLoading(true)
    try {
      const postData = {
        title: title.trim(),
        content: content.trim(),
        category_id: selectedCategory,
        tag_ids: selectedTags,
        is_published: isPublished
      }

      await onSave(postData)
    } catch (err) {
      console.error('Error saving post:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{post ? "Edit Blog Post" : "Create New Blog Post"}</DialogTitle>
        </DialogHeader>

        {dataLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin mr-2" />
            <span>Loading...</span>
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter post title..."
                disabled={loading}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">Category *</Label>
                <Select 
                  value={selectedCategory?.toString() || ""} 
                  onValueChange={(value) => setSelectedCategory(parseInt(value))}
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((cat) => (
                      <SelectItem key={cat.id} value={cat.id.toString()}>
                        {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="status">Status</Label>
                <Select 
                  value={isPublished ? "published" : "draft"} 
                  onValueChange={(value) => setIsPublished(value === "published")}
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="published">Published</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

          <div>
            <Label>Tags</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {selectedTags.map((tagId) => {
                const tag = availableTags.find(t => t.id === tagId)
                return tag ? (
                  <Badge key={tag.id} variant="secondary" className="flex items-center gap-1">
                    {tag.name}
                    <X className="w-3 h-3 cursor-pointer" onClick={() => removeTag(tag.id)} />
                  </Badge>
                ) : null
              })}
            </div>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag..."
                onKeyPress={(e) => e.key === "Enter" && addTag()}
                disabled={loading}
              />
              <Button type="button" onClick={addTag} variant="outline" disabled={loading}>
                Add
              </Button>
            </div>
            <div className="mt-2">
              <Label className="text-sm text-gray-600">Available Tags:</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {availableTags
                  .filter(tag => !selectedTags.includes(tag.id))
                  .map((tag) => (
                    <Badge 
                      key={tag.id} 
                      variant="outline" 
                      className="cursor-pointer hover:bg-gray-100"
                      onClick={() => toggleTag(tag.id)}
                    >
                      {tag.name}
                    </Badge>
                  ))
                }
              </div>
            </div>
          </div>

          <div>
            <Label htmlFor="content">Content * (Markdown supported)</Label>
            <Textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your blog post content here... You can use Markdown syntax, LaTeX for math ($$formula$$), and code blocks."
              rows={15}
              className="font-mono"
              disabled={loading}
            />
            <p className="text-sm text-gray-500 mt-1">
              Supports: Markdown, LaTeX math ($$formula$$), code blocks, and images
            </p>
          </div>

          <div className="flex justify-between">
            <div className="text-sm text-gray-500">
              Word count: {content.split(/\s+/).length} | Estimated read time: {calculateReadTime(content)}
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Saving...
                  </>
                ) : (
                  post ? "Update Post" : "Create Post"
                )}
              </Button>
            </div>
          </div>
        </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
