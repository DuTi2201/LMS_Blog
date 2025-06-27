"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, BookOpen, ChevronRight } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface BlogPost {
  id: number
  title: string
  content: string
  excerpt: string
  created_at: string
  updated_at: string
  published: boolean
  author_id: number
  category?: {
    id: number
    name: string
  }
  tags: {
    id: number
    name: string
  }[]
}

const gradients = [
  "from-blue-400 to-purple-600",
  "from-green-400 to-blue-500",
  "from-purple-400 to-pink-500",
  "from-orange-400 to-red-500",
  "from-red-400 to-pink-500",
  "from-yellow-400 to-orange-500",
]

export function BlogList() {
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchBlogPosts = async () => {
      try {
        setLoading(true)
        const response = await apiClient.getBlogPosts(0, 10)
        setBlogPosts(response.items || response)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch blog posts')
        console.error('Error fetching blog posts:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchBlogPosts()
  }, [])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const calculateReadTime = (content: string) => {
    const wordsPerMinute = 200
    const wordCount = content.split(' ').length
    const readTime = Math.ceil(wordCount / wordsPerMinute)
    return `${readTime} min read`
  }

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="overflow-hidden">
            <CardContent className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Error loading blog posts: {error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  if (blogPosts.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No blog posts found.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {blogPosts.map((post, index) => (
        <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
          <CardContent className="p-0">
            <div className="flex">
              <div className={`w-2 bg-gradient-to-b ${gradients[index % gradients.length]}`} />
              <div className="flex-1 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mb-2">
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(post.created_at)}</span>
                      </div>
                      {post.category && (
                        <div className="flex items-center space-x-1">
                          <BookOpen className="w-4 h-4" />
                          <span>{post.category.name}</span>
                        </div>
                      )}
                    </div>

                    <Link href={`/blog/${post.id}`}>
                      <h2 className="text-xl font-semibold text-gray-900 mb-3 hover:text-blue-600 transition-colors">
                        📚 {post.title}
                      </h2>
                    </Link>

                    <div className="flex flex-wrap gap-2 mb-3">
                      {post.tags.map((tag) => (
                        <Badge key={tag.id} variant="secondary" className="text-xs">
                          #{tag.name}
                        </Badge>
                      ))}
                    </div>

                    <p className="text-gray-600 mb-4">{post.excerpt || post.content.substring(0, 200) + '...'}</p>

                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{post.content.split(' ').length} words</span>
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{calculateReadTime(post.content)}</span>
                      </div>
                    </div>
                  </div>

                  <Link href={`/blog/${post.id}`}>
                    <ChevronRight className="w-5 h-5 text-gray-400 hover:text-gray-600 transition-colors" />
                  </Link>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
