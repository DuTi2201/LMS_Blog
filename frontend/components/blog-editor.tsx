"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { X, Loader2, Underline, AlignLeft, AlignCenter, AlignRight, Table, Calculator } from "lucide-react"
import { apiClient } from "@/lib/api"
import type { BlogPostData, Category, Tag } from "@/lib/api"
import dynamic from "next/dynamic"
import "katex/dist/katex.css"
import "@uiw/react-md-editor/markdown-editor.css"
import "@uiw/react-markdown-preview/markdown.css"
import "../styles/blog-editor.css"

// Dynamic import to avoid SSR issues
const MDEditor = dynamic(
  () => import("@uiw/react-md-editor").then((mod) => mod.default),
  { ssr: false }
)

// Dynamic import for better performance (removed unused EditorMarkdown)

// Custom toolbar commands
const getExtraCommands = () => {
  interface EditorState {
    selectedText?: string;
  }

  interface EditorAPI {
    replaceSelection: (text: string) => void;
  }

  const alignLeft = {
    name: 'align-left',
    keyCommand: 'align-left',
    buttonProps: { 'aria-label': 'Align left', title: 'Align left' },
    icon: <AlignLeft className="w-4 h-4" />,
    execute: (state: EditorState, api: EditorAPI) => {
      const modifyText = `<div style="text-align: left;">${state.selectedText || 'Left aligned text'}</div>`
      api.replaceSelection(modifyText)
    },
  }

  const alignCenter = {
    name: 'align-center',
    keyCommand: 'align-center',
    buttonProps: { 'aria-label': 'Align center', title: 'Align center' },
    icon: <AlignCenter className="w-4 h-4" />,
    execute: (state: EditorState, api: EditorAPI) => {
      const modifyText = `<div style="text-align: center;">${state.selectedText || 'Center aligned text'}</div>`
      api.replaceSelection(modifyText)
    },
  }

  const alignRight = {
    name: 'align-right',
    keyCommand: 'align-right',
    buttonProps: { 'aria-label': 'Align right', title: 'Align right' },
    icon: <AlignRight className="w-4 h-4" />,
    execute: (state: EditorState, api: EditorAPI) => {
      const modifyText = `<div style="text-align: right;">${state.selectedText || 'Right aligned text'}</div>`
      api.replaceSelection(modifyText)
    },
  }

  const underlineCommand = {
    name: 'underline',
    keyCommand: 'underline',
    buttonProps: { 'aria-label': 'Underline', title: 'Underline' },
    icon: <Underline className="w-4 h-4" />,
    execute: (state: EditorState, api: EditorAPI) => {
      const modifyText = `<u>${state.selectedText || 'underlined text'}</u>`
      api.replaceSelection(modifyText)
    },
  }

  const tableCommand = {
    name: 'table',
    keyCommand: 'table',
    buttonProps: { 'aria-label': 'Insert table', title: 'Insert table' },
    icon: <Table className="w-4 h-4" />,
    execute: (state: EditorState, api: EditorAPI) => {
      const tableText = `| Header 1 | Header 2 | Header 3 |\n|----------|----------|----------|\n| Cell 1   | Cell 2   | Cell 3   |\n| Cell 4   | Cell 5   | Cell 6   |`
      api.replaceSelection(tableText)
    },
  }

  const mathCommand = {
    name: 'math',
    keyCommand: 'math',
    buttonProps: { 'aria-label': 'Insert math formula', title: 'Insert math formula' },
    icon: <Calculator className="w-4 h-4" />,
    execute: (state: EditorState, api: EditorAPI) => {
      const mathText = state.selectedText || 'E = mc^2'
      const modifyText = `$$${mathText}$$`
      api.replaceSelection(modifyText)
    },
  }

  const colorCommand = {
    name: 'color',
    keyCommand: 'color',
    buttonProps: { 'aria-label': 'Text color', title: 'Text color' },
    icon: <span className="w-4 h-4 text-red-500 font-bold">A</span>,
    execute: (state: EditorState, api: EditorAPI) => {
      const modifyText = `<span style="color: #ff0000;">${state.selectedText || 'colored text'}</span>`
      api.replaceSelection(modifyText)
    },
  }

  const fontSizeCommand = {
    name: 'font-size',
    keyCommand: 'font-size',
    buttonProps: { 'aria-label': 'Font size', title: 'Font size' },
    icon: <span className="w-4 h-4 font-bold text-gray-700">Aa</span>,
    execute: (state: EditorState, api: EditorAPI) => {
      const modifyText = `<span style="font-size: 18px;">${state.selectedText || 'large text'}</span>`
      api.replaceSelection(modifyText)
    },
  }

  const highlightCommand = {
    name: 'highlight',
    keyCommand: 'highlight',
    buttonProps: { 'aria-label': 'Highlight text', title: 'Highlight text' },
    icon: <span className="w-4 h-4 bg-yellow-300 px-1 rounded text-xs font-bold">H</span>,
    execute: (state: EditorState, api: EditorAPI) => {
      const modifyText = `<mark style="background-color: #fef08a; padding: 2px 4px; border-radius: 3px;">${state.selectedText || 'highlighted text'}</mark>`
      api.replaceSelection(modifyText)
    },
  }

  return [alignLeft, alignCenter, alignRight, underlineCommand, tableCommand, mathCommand, colorCommand, fontSizeCommand, highlightCommand]
}

interface BlogPost {
  id: string
  title: string
  content: string
  author?: {
    id: string
    full_name: string
    email: string
  }
  created_at: string
  updated_at: string
  tags: {
    id: string
    name: string
  }[]
  category?: {
    id: string
    name: string
  }
  is_published: boolean
  word_count?: number
}

interface BlogEditorProps {
  post: BlogPost | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (postData: BlogPostData) => void
}

export function BlogEditor({ post, open, onOpenChange, onSave }: BlogEditorProps) {
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [isPublished, setIsPublished] = useState(false)
  const [newTag, setNewTag] = useState("")
  const [categories, setCategories] = useState<Category[]>([])
  const [availableTags, setAvailableTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(false)
  const [dataLoading, setDataLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setDataLoading(true)
        const [categoriesData, tagsData] = await Promise.all([
          apiClient.getBlogCategories(),
          apiClient.getBlogTags()
        ])
        setCategories(categoriesData as Category[])
        setAvailableTags(tagsData as Tag[])
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
      setSelectedTags(post.tags?.map(tag => tag.id) || [])
      setSelectedCategory(post.category?.id || null)
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
          const newTagData = (await apiClient.createBlogTag({ name: newTag.trim() })) as Tag
          setAvailableTags([...availableTags, newTagData as Tag])
          setSelectedTags([...selectedTags, newTagData.id])
        }
        setNewTag("")
      } catch (err) {
        console.error('Error adding tag:', err)
      }
    }
  }

  const removeTag = (tagId: string) => {
    setSelectedTags(selectedTags.filter((id) => id !== tagId))
  }

  const toggleTag = (tagId: string) => {
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

  const handleImageUpload = async (file: File): Promise<string> => {
    setUploading(true)
    try {
      const response = await apiClient.uploadFile(file, 'image')
      const imageUrl = response.file_info.url
      
      // Return markdown image syntax
      return `![${file.name}](${imageUrl})`
    } catch (error) {
      console.error('Error uploading image:', error)
      throw new Error('Failed to upload image')
    } finally {
      setUploading(false)
    }
  }

  const onImagePasted = async (dataTransfer: DataTransfer, setMarkdown: (markdown: string) => void, markdown: string) => {
    const files = Array.from(dataTransfer.files)
    const imageFiles = files.filter(file => file.type.startsWith('image/'))
    
    if (imageFiles.length > 0) {
      try {
        const imageMarkdowns = await Promise.all(
          imageFiles.map(file => handleImageUpload(file))
        )
        const newMarkdown = markdown + '\n\n' + imageMarkdowns.join('\n\n')
        setMarkdown(newMarkdown)
        setContent(newMarkdown)
      } catch {
        alert('Failed to upload images')
      }
    }
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
                  onValueChange={(value) => setSelectedCategory(value)}
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
            <Label htmlFor="content">Content * (Enhanced Rich Text Editor)</Label>
            <div className="mt-2 border rounded-lg overflow-hidden">
              <MDEditor
                value={content}
                onChange={(val) => setContent(val || "")}
                preview="edit"
                hideToolbar={false}
                visibleDragbar={false}
                extraCommands={getExtraCommands()}
                textareaProps={{
                  placeholder: "✍️ Start writing your amazing blog post here...\n\n🎨 **Rich Formatting Available:**\n• **Bold**, *Italic*, <u>Underline</u>\n• Text alignment (left, center, right)\n• 📊 Tables with easy formatting\n• 🧮 Math formulas: $$\\sum_{i=1}^{n} x_i = \\frac{n(n+1)}{2}$$\n• 🖼️ Images (drag & drop or paste)\n• 🎨 Text colors and styling\n• 📝 Code blocks with syntax highlighting\n• 📋 Lists, quotes, and more!",
                  style: { 
                    fontSize: 15, 
                    lineHeight: 1.7, 
                    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    padding: '16px',
                    border: 'none',
                    outline: 'none',
                    resize: 'none'
                  }
                }}
                data-color-mode="light"
                height={500}
                style={{
                  backgroundColor: '#fafafa',
                  border: 'none'
                }}
                onPaste={async (event) => {
                  await onImagePasted(event.clipboardData, (val) => setContent(val), content)
                }}
                onDrop={async (event) => {
                  event.preventDefault()
                  await onImagePasted(event.dataTransfer, (val) => setContent(val), content)
                }}
              />
            </div>
            
            {/* Enhanced Help Section */}
            <div className="mt-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-gray-800 mb-2">🚀 Enhanced Editor Features</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                    <div className="space-y-1">
                      <p>• <strong>Text Formatting:</strong> Bold, Italic, Underline</p>
                      <p>• <strong>Alignment:</strong> Left, Center, Right</p>
                      <p>• <strong>Colors:</strong> Custom text colors</p>
                    </div>
                    <div className="space-y-1">
                      <p>• <strong>Tables:</strong> Professional formatting</p>
                      <p>• <strong>Math:</strong> LaTeX formulas ($$formula$$)</p>
                      <p>• <strong>Media:</strong> Drag & drop images</p>
                    </div>
                  </div>
                </div>
                {uploading && (
                  <div className="flex items-center text-sm text-blue-600 ml-4">
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    <span className="font-medium">Uploading image...</span>
                  </div>
                )}
              </div>
            </div>
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
