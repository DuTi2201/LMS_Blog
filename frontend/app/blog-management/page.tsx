"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Eye, Edit, Trash2, Plus, Loader2 } from "lucide-react"
import { BlogEditor } from "@/components/blog-editor"
import { apiClient } from "@/lib/api"
import type { BlogPost, BlogPostData, User } from "@/lib/api"

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
        const userData: User = await apiClient.getCurrentUser()
        setUser(userData)
        
        // Fetch blog posts
        const postsData = await apiClient.getBlogPosts()
        const posts: BlogPost[] = Array.isArray(postsData) ? postsData : (postsData as { items?: BlogPost[] }).items || []
        const postsWithWordCount = posts.map(post => ({
          ...post,
          word_count: calculateWordCount(post.content)
        }))
        setPosts(postsWithWordCount)
      } catch (err: unknown) {
        console.error('Error fetching data:', err)
        if (err instanceof Error) {
          setError(`Failed to load blog posts: ${err.message}`)
        } else {
          setError('An unknown error occurred while loading blog posts')
        }

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

  const handleEditPost = (post: BlogPost): void => {
    setEditingPost(post)
    setIsEditorOpen(true)
  }

  const calculateWordCount = (content: string): number => {
    if (!content) return 0
    return content.trim().split(/\s+/).filter(word => word.length > 0).length
  }

  const handleViewPost = (postId: string): void => {
    window.open(`/blog/${postId}`, '_blank')
  }

  const handleDeletePost = async (postId: string): Promise<void> => {
    if (!confirm('Are you sure you want to delete this post?')) {
      return
    }
    
    try {
      await apiClient.deleteBlogPost(postId)
      setPosts(posts.filter((post: BlogPost) => post.id !== postId))
    } catch (error) {
      console.error('Error deleting post:', error)
      alert('Failed to delete post. Please try again.')
    }
  }

  const handleSavePost = async (postData: BlogPostData): Promise<void> => {
    try {
      let savedPost: BlogPost
      
      if (editingPost) {
        // Update existing post
        savedPost = await apiClient.updateBlogPost(editingPost.id, postData)
        const postWithWordCount: BlogPost = {
          ...savedPost,
          word_count: calculateWordCount(savedPost.content)
        }
        setPosts(posts.map((post: BlogPost) => 
          post.id === editingPost.id ? postWithWordCount : post
        ))
      } else {
        // Create new post
        savedPost = await apiClient.createBlogPost(postData)
        const postWithWordCount: BlogPost = {
          ...savedPost,
          word_count: calculateWordCount(savedPost.content)
        }
        setPosts([postWithWordCount, ...posts])
      }
      
      setIsEditorOpen(false)
      setEditingPost(null)
    } catch (error) {
      console.error('Error saving post:', error)
      alert('Failed to save post. Please try again.')
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
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-red-600">{error}</div>
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
            posts.map((post: BlogPost) => (
              <Card key={post.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{post.title}</CardTitle>
                      <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                        <span>By {post.author?.full_name || 'Unknown Author'}</span>
                        <span>{formatDate(post.created_at)}</span>
                        <Badge variant={post.is_published ? "default" : "secondary"}>
                          {post.is_published ? "published" : "draft"}
                        </Badge>
                        <span>{post.word_count || 0} words</span>
                        <span>{calculateReadTime(post.word_count || 0)}</span>
                      </div>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {post.category && <Badge variant="outline">{post.category.name}</Badge>}
                        {post.tags.map((tag: { id: string; name: string }) => (
                          <Badge key={tag.id} variant="secondary" className="text-xs">
                            #{tag.name}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex space-x-2">
                      <Button variant="ghost" size="sm" onClick={() => handleViewPost(post.id)}>
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleEditPost(post)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      {(user?.role === "instructor" || post.author?.id === user?.id) && (
                        <Button variant="ghost" size="sm" onClick={() => handleDeletePost(post.id)}>
                          <Trash2 className="w-4 h-4 text-red-500" />
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
