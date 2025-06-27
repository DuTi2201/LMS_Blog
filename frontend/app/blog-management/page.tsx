"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, Edit, Trash2, Eye, Loader2 } from "lucide-react"
import { BlogEditor } from "@/components/blog-editor"
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

interface User {
  id: number
  email: string
  full_name: string
  role: string
}

export default function BlogManagementPage() {
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [editingPost, setEditingPost] = useState<BlogPost | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Fetch user data
        const userData = await apiClient.getCurrentUser()
        setUser(userData)
        
        // Fetch blog posts
        const postsData = await apiClient.getBlogPosts()
        setPosts(postsData)
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load blog posts')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const calculateReadTime = (wordCount: number) => {
    const wordsPerMinute = 200
    const minutes = Math.ceil(wordCount / wordsPerMinute)
    return `${minutes} min read`
  }

  const handleCreatePost = () => {
    setEditingPost(null)
    setIsEditorOpen(true)
  }

  const handleEditPost = (post: BlogPost) => {
    setEditingPost(post)
    setIsEditorOpen(true)
  }

  const handleDeletePost = async (postId: number) => {
    try {
      await apiClient.deleteBlogPost(postId)
      setPosts(posts.filter((p) => p.id !== postId))
    } catch (err) {
      console.error('Error deleting post:', err)
      setError('Failed to delete post')
    }
  }

  const handleSavePost = async (postData: any) => {
    try {
      if (editingPost) {
        // Update existing post
        const updatedPost = await apiClient.updateBlogPost(editingPost.id, postData)
        setPosts(posts.map((p) => (p.id === editingPost.id ? updatedPost : p)))
      } else {
        // Create new post
        const newPost = await apiClient.createBlogPost(postData)
        setPosts([newPost, ...posts])
      }
      setIsEditorOpen(false)
    } catch (err) {
      console.error('Error saving post:', err)
      setError('Failed to save post')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin" />
            <span className="ml-2">Loading blog posts...</span>
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
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
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
          <h1 className="text-3xl font-bold text-gray-900">Blog Management</h1>
          <Button onClick={handleCreatePost}>
            <Plus className="w-4 h-4 mr-2" />
            Create New Post
          </Button>
        </div>

        <div className="grid gap-6">
          {posts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 mb-4">No blog posts found</p>
              <Button onClick={handleCreatePost}>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Post
              </Button>
            </div>
          ) : (
            posts.map((post) => (
              <Card key={post.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{post.title}</CardTitle>
                      <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                        <span>By {post.author.full_name}</span>
                        <span>{formatDate(post.created_at)}</span>
                        <Badge variant={post.is_published ? "default" : "secondary"}>
                          {post.is_published ? "published" : "draft"}
                        </Badge>
                        <span>{post.word_count} words</span>
                        <span>{calculateReadTime(post.word_count)}</span>
                      </div>
                      <div className="flex flex-wrap gap-2 mb-3">
                        <Badge variant="outline">{post.category.name}</Badge>
                        {post.tags.map((tag) => (
                          <Badge key={tag.id} variant="secondary" className="text-xs">
                            #{tag.name}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex space-x-2">
                      <Button variant="ghost" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleEditPost(post)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      {(user?.role === "admin" || post.author.id === user?.id) && (
                        <Button variant="ghost" size="sm" onClick={() => handleDeletePost(post.id)}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 line-clamp-3">
                    {post.content.replace(/[#*]/g, "").substring(0, 200)}...
                  </p>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      <BlogEditor post={editingPost} open={isEditorOpen} onOpenChange={setIsEditorOpen} onSave={handleSavePost} />
    </div>
  )
}
